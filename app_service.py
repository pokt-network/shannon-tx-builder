import json
import random
import string
import subprocess

import streamlit as st

from helpers import present_tx_result
from poktrolld import (
    CMD_SHARE_JSON_OUTPUT,
    CMD_SHARED_ARGS_KEYRING,
    CMD_SHARED_ARGS_NODE,
    EXPLORER_URL,
    POCKET_RPC_NODE,
    POKTROLLD_BIN_PATH,
    is_localnet,
)


def add_service_tab():
    st.header("Create Service")
    st.write("Update the parameters below to create a new service.")

    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    svc_id = f"svc_{random_suffix}"
    service_id = st.text_input("Service ID", svc_id)

    service_name = st.text_input("Service Name", f"name for {svc_id}")
    compute_units = st.number_input("Compute Units To Token Multiplier", min_value=1, value=7)

    service_owner_account = "faucet" if not st.session_state.get("key_name") else st.session_state["key_name"]
    service_owner = st.text_input("Service Owner (account to create the service)", service_owner_account)

    # Create a new service on-chain
    if st.button("Create Service"):
        # poktrolld tx service add-service <service_id> <service_name> <compute_units> --from <account> [flags]
        cmd_service_add = (
            [
                POKTROLLD_BIN_PATH,
                "tx",
                "service",
                "add-service",
                f'"{service_id}"',
                f'"{service_name}"',
                str(compute_units),
                "--from",
                service_owner,
                "--yes",
            ]
            + CMD_SHARE_JSON_OUTPUT
            + CMD_SHARED_ARGS_NODE
            + CMD_SHARED_ARGS_KEYRING
        )
        result = subprocess.run(" ".join(cmd_service_add), capture_output=True, text=True, shell=True)

        # Check the status of the service creation
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            st.success(f"Service creation tx successfully sent!")
            present_tx_result(tx_hash)

            st.session_state["svc_id"] = service_id

            st.write("You can query the service like so:")
            st.code(f"poktrolld query service show-service {svc_id} \\\n --node {POCKET_RPC_NODE}")
            st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error creating service {service_id}: {result.stderr}")
