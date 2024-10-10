import json
import subprocess

import streamlit as st

from faucet import import_faucet_key
from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_NODE, EXPLORER_URL, POKTROLLD_BIN_PATH


def add_supplier_tab():

    default_supplier = st.session_state.get("address", "supplier")
    default_key_name = st.session_state.get("key_name", "supplier_key")

    st.header("Create Supplier")
    supplier_address = st.text_input("Supplier Address", default_supplier)
    relay_miner_url = st.text_input("Relay Miner URL", " http://relayminer:8545")
    stake_amount = st.number_input("Stake Amount", min_value=1, value=1000069)

    st.subheader("Supplier Configuration")
    st.code(
        language="yaml",
        body=f"""
owner_address: {supplier_address}
operator_address: {supplier_address}
stake_amount: {stake_amount}upokt
default_rev_share_percent:
  - {supplier_address}: 100
services:
  - service_id: anvil
    endpoints:
      - publicly_exposed_url: {relay_miner_url}
        rpc_type: JSON_RPC
            """,
    )

    # poktrolld --home=$(POKTROLLD_HOME) tx supplier stake-supplier -y --config $(POKTROLLD_HOME)/config/$(SERVICES) --keyring-backend test --from $(SUPPLIER) --node $(POCKET_NODE)


#     add_service_cmd = (
#         [
#             POKTROLLD_BIN_PATH,
#             "tx",
#             "service",
#             "add-service",
#             f'"{service_id}"',
#             f'"{service_name}"',
#             str(compute_units),
#             "--from",
#             account,
#             "--yes",
#         ]
#         + CMD_SHARE_JSON_OUTPUT
#         + CMD_SHARED_ARGS_NODE
#     )
#     if st.button("Create Service"):
#         result = subprocess.run(" ".join(add_service_cmd), capture_output=True, text=True, shell=True)
#         print(result)
#         tx_response = json.loads(result.stdout)
#         tx_hash = tx_response.get("txhash", "N/A")
#         if result.returncode == 0:
#             st.success(f"Service creation tx successfully sent!")
#             st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
#             st.write(
#                 f"**Transaction Hash**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})"
#             )
#         else:
#             st.error(f"Error creating service {service_id}: {result.stderr}")

#     st.header("Prepare Relay Miner")
#     st.code(
#         language="yaml",
#         body=f"""
# signing_key_name: {default_key_name}
# smt_store_path: /root/.poktroll/smt
# metrics:
#   enabled: true
#   addr: :9090
# pocket_node:
#   query_node_rpc_url: tcp://127.0.0.1:26657
#   query_node_grpc_url: tcp://127.0.0.1:9090
#   tx_node_rpc_url: tcp://127.0.0.1:26657
# suppliers:
#   - service_id: anvil
#     listen_url: http://localhost:6942
#     service_config:
#       backend_url: http://localhost:8081
#       publicly_exposed_endpoints:
#         - localhost
# pprof:
#   enabled: false
#   addr: localhost:6060
# ping:
#   enabled: false
#   addr: localhost:8082""",
#     )
