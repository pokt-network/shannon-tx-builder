import json
import subprocess
import urllib.parse

import streamlit as st

from faucet import FAUCET_ADDRESS, FAUCET_NAME
from helpers import present_tx_result, write_to_temp_yaml_file
from poktrolld import (
    CMD_ARG_FEES,
    CMD_ARGS_JSON,
    CMD_ARGS_KEYRING,
    CMD_ARGS_NODE,
    GRPC_NODE,
    POKTROLLD_BIN_PATH,
    POKTROLLD_HOME,
    RPC_NODE,
    is_localnet,
)


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
        "Relay Miner URL (the offchain URL where the services will be accessible)", "http://localhost:8500"
    )
    st.session_state["relay_miner_url"] = relay_miner_url
    # TODO_IMPROVE: Set the minimum based on the onchain governance parameters
    stake_amount = st.number_input(
        "Stake Amount (the amount the supplier puts into escrow to provide services)",
        min_value=1,
        value=1000069,
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
    button_clicked = st.button("Stake Supplier")
    if button_clicked or st.session_state.get("supplier_staked", False):
        supplier_stake_config = write_to_temp_yaml_file(code)
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
            + CMD_ARGS_JSON
            + CMD_ARGS_NODE
            + CMD_ARGS_KEYRING
            + CMD_ARG_FEES
        )
        if button_clicked:
            result = subprocess.run(" ".join(cmd_stake_supplier), capture_output=True, text=True, shell=True)
        else:
            result = st.session_state["supplier_stake_result"]

        # Check the status of the supplier creation transaction
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            if tx_response.get("code", -1) == 0:
                st.session_state["supplier_staked"] = True
                st.session_state["supplier_stake_result"] = result

                st.success(f"Supplier creation tx successfully sent!")
                present_tx_result(tx_hash)

                st.write("You can query the supplier like so:")
                st.code(
                    f"poktrolld query supplier show-supplier {supplier_addr} \\\n --node {RPC_NODE} --output json | jq"
                )

                # TODO: Configure this number once we query the block time from on-chain
                st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
            else:
                raw_log = tx_response.get("raw_log", "raw_log unavailable")
                st.error(f"Error funding address: {raw_log}")
        else:
            st.error(f"Error sending create supplier transaction: {result.stderr}")


def configure_relay_miner():
    default_smt_store_path = "/tmp/poktroll/smt"
    # default_smt_store_path = "~/.poktroll/smt" if is_localnet() else "/root/.poktroll/smt"

    supplier_key_name = st.session_state["supplier_key_name"]
    supplier_service_id = st.session_state["supplier_service_id"]

    relay_miner_url = st.session_state.get("relay_miner_url", "http://localhost:6942")
    relay_miner_url_parsed = urllib.parse.urlsplit(relay_miner_url)
    publically_exposed_hostname = relay_miner_url_parsed.hostname

    smt_store_path = st.text_input(
        "The directory where the RelayMiner stores the SMT (make sure to run mkdir -p)", default_smt_store_path
    )
    backend_url = st.text_input("The URL where the service backend is accessible", "http://localhost:8547")
    listen_url = st.text_input("The URL where the RelayMiner listens for incoming requests", "http://localhost:8500")

    st.subheader("3. Configure the offchain RelayMiner")
    code = f"""
default_signing_key_names: [{supplier_key_name}]
smt_store_path: {smt_store_path}
metrics:
  enabled: true
  addr: :9091
pocket_node:
  query_node_rpc_url: {RPC_NODE}
  query_node_grpc_url: {GRPC_NODE}
  tx_node_rpc_url: {RPC_NODE}
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

    if is_localnet():
        if st.button("Write RelayMiner configs to disk") or st.session_state.get(
            "relayminer_config_file_written", False
        ):
            relayminer_config_file = write_to_temp_yaml_file(code)
            st.subheader("4. Start the offchain RelayMiner")
            cmd_code = f"{POKTROLLD_BIN_PATH} relayminer \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config={relayminer_config_file}"
            st.code(
                language="bash",
                body=cmd_code,
            )
            st.session_state["relayminer_config_file_written"] = True
    else:
        relayminer_config_file = write_to_temp_yaml_file(code)
        with open(relayminer_config_file, "r") as file:
            st.download_button(
                label="Download RelayMiner Config File",
                data=file,
                file_name="relayminer_config.yaml",
                mime="text/toml",
            )
            st.subheader("4. Start the offchain RelayMiner")
            cmd_code = f"{POKTROLLD_BIN_PATH} relayminer \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config=relayminer_config.yaml"
            st.code(cmd_code, language="bash")
