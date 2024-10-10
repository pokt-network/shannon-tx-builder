import json
import subprocess

import streamlit as st

from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_NODE, EXPLORER_URL, POKTROLLD_BIN_PATH


def add_service_tab():
    st.header("Create Service")
    st.write("Update the parameters below to create a new service.")
    service_id = st.text_input("Service ID", "svc-id")
    service_name = st.text_input("Service Name", "svc-name")
    compute_units = st.number_input("Compute Units To Token Multiplier", min_value=1, value=18)
    account = st.text_input("Account (to create the service)", "faucet")
    add_service_cmd = (
        [
            POKTROLLD_BIN_PATH,
            "tx",
            "service",
            "add-service",
            f'"{service_id}"',
            f'"{service_name}"',
            str(compute_units),
            "--from",
            account,
            "--yes",
        ]
        + CMD_SHARE_JSON_OUTPUT
        + CMD_SHARED_ARGS_NODE
    )
    if st.button("Create Service"):
        result = subprocess.run(" ".join(add_service_cmd), capture_output=True, text=True, shell=True)
        print(result)
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            st.success(f"Service creation tx successfully sent!")
            st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
            st.write(
                f"**Transaction Hash**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})"
            )
        else:
            st.error(f"Error creating service {service_id}: {result.stderr}")

    st.header("Query Service")
    query_service_cmd = (
        [
            POKTROLLD_BIN_PATH,
            "query",
            "service",
            "show-service",
            service_id,
        ]
        + CMD_SHARED_ARGS_NODE
        + CMD_SHARE_JSON_OUTPUT
    )

    if st.button(f"Query Service {service_id}"):
        result = subprocess.run(" ".join(query_service_cmd), capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            service = json.loads(result.stdout)
            st.success(f"Service {service_id} successfully queried!")
            st.write(service)
        else:
            st.error(f"Error querying service {service_id}: {result.stderr}")
