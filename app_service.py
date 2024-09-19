import json
import subprocess

import streamlit as st

from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_KEYRING, CMD_SHARED_ARGS_NODE, POKTROLLD_PATH


def add_tab_service():
    st.header("Create Service")
    st.write("Update the parameters below to create a new service.")
    service_id = st.text_input("Service ID", "svc-id")
    service_name = st.text_input("Service Name", "svc-name")
    compute_units = st.number_input("Compute Units To Token Multiplier", min_value=1, value=18)
    account = st.text_input("Account (to create the service)", "faucet")
    add_service_cmd = (
        [
            POKTROLLD_PATH,
            "tx",
            "service",
            "add-service",
            service_id,
            service_name,
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
        if result.returncode == 0:
            st.success(f"Service {service_id} successfully created!")
        else:
            st.error(f"Error creating service {service_id}: {result.stderr}")

    st.header("Query Service")
    query_service_cmd = (
        [
            POKTROLLD_PATH,
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
