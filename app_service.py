import json
import random
import string
import subprocess

import streamlit as st

from faucet import FAUCET_NAME
from helpers import present_tx_result
from poktrolld import CMD_ARG_FEES, CMD_ARGS_JSON, CMD_ARGS_KEYRING, CMD_ARGS_NODE, POKTROLLD_BIN_PATH, RPC_NODE


def add_service_tab():
    st.header("Create a new Service")

    st.subheader("1. Configure the Service")
    st.write("Update the parameters below to create a new service.")

    st.warning("If you just created and funded new account, it is the default for the service owner below.")

    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    default_service_id = st.session_state.get("service_id", f"svc_{random_suffix}")
    service_id = st.text_input("Service ID (the unique identifier for the service)", default_service_id)
    st.session_state["service_id"] = service_id
    st.session_state["service_id_created_onchain"] = st.session_state.get("service_id_created_onchain", False)

    service_name = st.text_input("Service Name (semantic metadata to describe the service)", f"name for {service_id}")
    compute_units = st.number_input(
        "Compute Units To Token Multiplier (how expensive is each request for this service)", min_value=1, value=7
    )

    service_owner_account = st.session_state.get("key_name", FAUCET_NAME)
    service_owner = st.text_input(
        "Service Owner (account that creates, owns and maintains the service)", service_owner_account
    )

    st.subheader("2. Create the Service")

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
            + CMD_ARGS_JSON
            + CMD_ARGS_NODE
            + CMD_ARGS_KEYRING
            + CMD_ARG_FEES
        )
        result = subprocess.run(" ".join(cmd_service_add), capture_output=True, text=True, shell=True)
        # print(result)

        # Check the status of the service creation
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            if tx_response.get("code", -1) == 0:
                st.success(f"Service creation tx successfully sent!")
                present_tx_result(tx_hash)

                st.session_state["service_id"] = service_id
                st.session_state["service_id_created_onchain"] = True

                st.write("You can query the service like so:")
                st.code(f"poktrolld query service show-service {service_id} \\\n --node {RPC_NODE} --output json | jq")

                # TODO: Configure this number once we query the block time from on-chain
                st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
            else:
                raw_log = tx_response.get("raw_log", "raw_log unavailable")
                st.error(f"Error funding address: {raw_log}")
        else:
            st.error(f"Error creating service {service_id}: {result.stderr}")
