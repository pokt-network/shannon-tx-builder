import json
import subprocess
import tempfile

import streamlit as st

from helpers import present_tx_result
from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_NODE, POCKET_RPC_NODE, POKTROLLD_BIN_PATH, POKTROLLD_HOME


def add_supplier_tab():
    stake_supplier()
    configure_relay_miner()


def stake_supplier():
    default_supplier_addr = st.session_state.get("address", "supplier")
    default_supplier_key_name = st.session_state.get("key_name", "key_name")
    default_svc = st.session_state.get("svc_id", "anvil")

    st.header("Prepare & Stake Supplier")
    supplier_addr = st.text_input("Supplier Address", default_supplier_addr)
    supplier_key_name = st.text_input("Supplier Key Name", default_supplier_key_name)
    supplier_service_id = st.text_input("Supplier Service ID", default_svc)
    relay_miner_url = st.text_input("Relay Miner URL", "http://relayminer:8545")
    stake_amount = st.number_input("Stake Amount", min_value=1, value=1000069)

    st.subheader("Supplier Configuration")
    code = f"""owner_address: {supplier_addr}
operator_address: {supplier_addr}
stake_amount: {stake_amount}upokt
default_rev_share_percent:
  {supplier_addr}: 100
services:
  - service_id: {supplier_service_id}
    endpoints:
      - publicly_exposed_url: {relay_miner_url}
        rpc_type: JSON_RPC"""
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
        print("OLSH", " ".join(cmd_stake_supplier))
        result = subprocess.run(" ".join(cmd_stake_supplier), capture_output=True, text=True, shell=True)

        # Check the status of the service creation
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            st.success(f"Service creation tx successfully sent!")
            present_tx_result(tx_hash)

            st.write("You can query the supplier like so:")
            st.code(f"poktrolld query service show-supplier {supplier_addr} \\\n --node {POCKET_RPC_NODE}")
            st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error creating service {supplier_service_id}: {result.stderr}")


def configure_relay_miner():
    default_key_name = st.session_state.get("key_name", "key_name")

    st.header("Prepare Relay Miner")
    code = f"""
signing_key_name: {default_key_name}
smt_store_path: /root/.poktroll/smt
metrics:
  enabled: true
  addr: :9090
pocket_node:
  query_node_rpc_url: tcp://127.0.0.1:26657
  query_node_grpc_url: tcp://127.0.0.1:9090
  tx_node_rpc_url: tcp://127.0.0.1:26657
suppliers:
  - service_id: anvil
    listen_url: http://localhost:6942
    service_config:
      backend_url: http://localhost:8081
      publicly_exposed_endpoints:
        - localhost
pprof:
  enabled: false
  addr: localhost:6060
ping:
  enabled: false
  addr: localhost:8082"""
    st.code(
        language="yaml",
        body=code,
    )

    cmd_code = f"""
{POKTROLLD_BIN_PATH} \
    relayminer \
    --home {POKTROLLD_HOME} \
    --keyring-backend=test \
    --config=/home/pocket/.poktroll/config/relayminer_config.yaml
"""
    st.code(
        language="bash",
        body=cmd_code,
    )


# Binary command configs
POKTROLLD_BIN_PATH = "./poktrolld"
CMD_SHARE_JSON_OUTPUT = ["--output", "json"]

CMD_SHARED_ARGS_KEYRING = ["--home", POKTROLLD_HOME, "--keyring-backend", "test"]


def write_to_temp_file(data) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(data.encode("utf-8"))  # Write data to the file
        tmp_file_path = tmp_file.name  # Get the path to the file
    return tmp_file_path
