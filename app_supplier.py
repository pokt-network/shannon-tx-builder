import ast
import json
import subprocess
import tempfile
import urllib.parse

import streamlit as st

from faucet import FAUCET_ADDRESS, FAUCET_NAME
from helpers import present_tx_result
from poktrolld import (
    CMD_SHARE_JSON_OUTPUT,
    CMD_SHARED_ARGS_NODE,
    POCKET_GRPC_NODE,
    POCKET_RPC_NODE,
    POKTROLLD_BIN_PATH,
    POKTROLLD_HOME,
    is_localnet,
)


def write_to_temp_file(data) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(data.encode("utf-8"))  # Write data to the file
        tmp_file_path = tmp_file.name  # Get the path to the file
    return tmp_file_path


def add_supplier_tab():
    stake_supplier()
    configure_relay_miner()


def stake_supplier():
    default_supplier_addr = st.session_state.get("address", FAUCET_ADDRESS)
    default_supplier_key_name = st.session_state.get("key_name", FAUCET_NAME)
    default_service = (
        "anvil" if not st.session_state["service_id_created_onchain"] else st.session_state.get("service_id")
    )

    st.header("Prepare & Stake a Supplier")

    st.subheader("1. Configure the onchain Supplier")
    st.warning("If you just created and funded new account, it is the default for the supplier below.")

    supplier_addr = st.text_input(
        "Supplier Address (the address of the supplier providing services)", default_supplier_addr
    )
    st.session_state["supplier_addr"] = supplier_addr
    supplier_key_name = st.text_input(
        "Supplier Key Name (the name associated with the supplier in your local keyring)", default_supplier_key_name
    )
    st.session_state["supplier_key_name"] = supplier_key_name
    supplier_service_id = st.text_input(
        "Supplier Service ID (the onchain unique service ID for which services are provided)", default_service
    )
    st.session_state["supplier_service_id"] = supplier_service_id
    relay_miner_url = st.text_input(
        "Relay Miner URL (the offchain URL where the services will be accessible)", "http://relayminer:8545"
    )
    st.session_state["relay_miner_url"] = relay_miner_url
    stake_amount = st.number_input(
        "Stake Amount (the amount the supplier puts into escrow to provide services)", min_value=1, value=1000069
    )

    st.subheader("2. Stake the onchain Supplier")
    code = f"""owner_address: {supplier_addr}
operator_address: {supplier_addr}
stake_amount: {stake_amount}upokt
default_rev_share_percent:
  {supplier_addr}: 100
services:
  - service_id: "{supplier_service_id}"
    endpoints:
      - publicly_exposed_url: {relay_miner_url}
        rpc_type: JSON_RPC
"""
    st.code(
        language="yaml",
        body=code,
    )

    # Create a new service on-chain
    if st.button("Stake Supplier"):
        supplier_stake_config = write_to_temp_file(code)
        # poktrolld tx service add-service <service_id> <service_name> <compute_units> --from <account> [flags]
        cmd_stake_supplier = (
            [
                POKTROLLD_BIN_PATH,
                "tx",
                "supplier",
                "stake-supplier",
                "--config",
                supplier_stake_config,
                "--from",
                supplier_key_name,
                "--yes",
            ]
            + CMD_SHARE_JSON_OUTPUT
            + CMD_SHARED_ARGS_NODE
            + CMD_SHARED_ARGS_KEYRING
        )
        result = subprocess.run(" ".join(cmd_stake_supplier), capture_output=True, text=True, shell=True)

        # Check the status of the supplier creation transaction
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            tx_code = tx_response.get("code", -1)
            if tx_code != 0:
                tx_log = tx_response.get("raw_log", "raw_log unavailable")
                st.error(f"Error submitting create supplier transaction: {tx_log}")
            else:
                st.success(f"Supplier creation tx successfully sent!")
                present_tx_result(tx_hash)

                st.write("You can query the supplier like so:")
                st.code(
                    f"poktrolld query supplier show-supplier {supplier_addr} \\\n --node {POCKET_RPC_NODE} --output json | jq"
                )

                # TODO: Configure this number once we query the block time from on-chain
                st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error sending create supplier transaction: {result.stderr}")


def configure_relay_miner():
    default_smt_store_path = "~/.poktroll/smt" if is_localnet() else "/root/.poktroll/smt"

    supplier_key_name = st.session_state["supplier_key_name"]
    supplier_service_id = st.session_state["supplier_service_id"]

    relay_miner_url = st.session_state.get("relay_miner_url", "http://localhost:6942")
    relay_miner_url_parsed = urllib.parse.urlsplit(relay_miner_url)
    publically_exposed_hostname = relay_miner_url_parsed.hostname

    smt_store_path = st.text_input("The directory where the RelayMiner stores the SMT", default_smt_store_path)
    backend_url = st.text_input("The URL where the service backend is accessible", "http://localhost:8547")
    listen_url = st.text_input("The URL where the RelayMiner listens for incoming requests", "http://localhost:8500")

    st.subheader("3. Configure the offchain RelayMiner")
    code = f"""
default_signing_key_names: [{supplier_key_name}]
smt_store_path: {smt_store_path}
metrics:
  enabled: true
  addr: :9090
pocket_node:
  query_node_rpc_url: {POCKET_RPC_NODE}
  query_node_grpc_url: {POCKET_GRPC_NODE}
  tx_node_rpc_url: {POCKET_RPC_NODE}
suppliers:
  - service_id: {supplier_service_id}
    listen_url: {listen_url}
    service_config:
      backend_url: {backend_url}
      publicly_exposed_endpoints:
        - {publically_exposed_hostname}
pprof:
  enabled: false
  addr: localhost:6060
ping:
  enabled: false
  addr: localhost:8082
"""
    st.code(
        language="yaml",
        body=code,
    )

    if not is_localnet():
        if st.button("Write configs to disk"):
            relayminer_config_file = write_to_temp_file(code)
            st.subheader("4. Start the offchain RelayMiner")
            cmd_code = f"{POKTROLLD_BIN_PATH} relayminer \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config={relayminer_config_file}"
            st.code(
                language="bash",
                body=cmd_code,
            )
    else:
        relayminer_config_file = write_to_temp_file(code)
        with open(relayminer_config_file, "r") as file:
            st.download_button(
                label="Download Config File", data=file, file_name="relayminer_config.toml", mime="text/toml"
            )
            st.subheader("4. Start the offchain RelayMiner")
            cmd_code = f"{POKTROLLD_BIN_PATH} relayminer \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config=PATH_TO_CONFIGS_FILE"
            st.code(cmd_code, language="bash")
