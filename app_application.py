import json
import subprocess
import urllib.parse

import streamlit as st

from faucet import FAUCET_ADDRESS, FAUCET_NAME
from helpers import present_tx_result, write_to_temp_yaml_file
from poktrolld import (
    CMD_SHARE_JSON_OUTPUT,
    CMD_SHARED_ARGS_KEYRING,
    CMD_SHARED_ARGS_NODE,
    POCKET_GRPC_NODE,
    POCKET_RPC_NODE,
    POKTROLLD_BIN_PATH,
    POKTROLLD_HOME,
    is_localnet,
)


def add_application_tab():
    stake_application()
    configure_appgate_server()


def stake_application():
    default_application_addr = st.session_state.get("address", FAUCET_ADDRESS)
    default_application_key_name = st.session_state.get("key_name", FAUCET_NAME)
    default_service = (
        "anvil" if not st.session_state["service_id_created_onchain"] else st.session_state.get("service_id")
    )

    st.header("Prepare & Stake a Application")

    st.subheader("1. Configure the onchain Application")
    st.warning("If you just created and funded new account, it is the default for the application below.")

    application_addr = st.text_input(
        "Application Address (the address of the application providing services)", default_application_addr
    )
    st.session_state["application_addr"] = application_addr
    application_key_name = st.text_input(
        "Application Key Name (the name associated with the application in your local keyring)",
        default_application_key_name,
    )
    st.session_state["application_key_name"] = application_key_name
    application_service_id = st.text_input(
        "Application Service ID (the onchain unique service ID for which services are provided)", default_service
    )
    st.session_state["application_service_id"] = application_service_id
    # TODO_IMPROVE: Set the minimum based on the onchain governance parameters
    stake_amount = st.number_input(
        "Stake Amount (the amount the application puts into escrow to provide services)", min_value=1, value=100000069
    )

    st.subheader("2. Stake the onchain Application")
    code = f"""stake_amount: {stake_amount}upokt
service_ids:
  - {application_service_id}
"""
    st.code(
        language="yaml",
        body=code,
    )

    # Create a new service on-chain
    button_clicked = st.button("Stake Application")
    if button_clicked or st.session_state.get("application_staked", False):
        application_stake_config = write_to_temp_yaml_file(code)
        cmd_stake_application = (
            [
                POKTROLLD_BIN_PATH,
                "tx",
                "application",
                "stake-application",
                "--config",
                application_stake_config,
                "--from",
                application_key_name,
                "--yes",
            ]
            + CMD_SHARE_JSON_OUTPUT
            + CMD_SHARED_ARGS_NODE
            + CMD_SHARED_ARGS_KEYRING
        )
        if button_clicked:
            result = subprocess.run(" ".join(cmd_stake_application), capture_output=True, text=True, shell=True)
        else:
            result = st.session_state["application_stake_result"]

        # Check the status of the application creation transaction
        tx_response = json.loads(result.stdout)
        tx_hash = tx_response.get("txhash", "N/A")
        if result.returncode == 0:
            tx_code = tx_response.get("code", -1)
            if tx_code != 0:
                tx_log = tx_response.get("raw_log", "raw_log unavailable")
                st.error(f"Error submitting create application transaction: {tx_log}")
            else:
                st.session_state["application_staked"] = True
                st.session_state["application_stake_result"] = result

                st.success(f"Application creation tx successfully sent!")
                present_tx_result(tx_hash)

                st.write("You can query the application like so:")
                st.code(
                    f"poktrolld query application show-application {application_addr} \\\n --node {POCKET_RPC_NODE} --output json | jq"
                )

                # TODO: Configure this number once we query the block time from on-chain
                st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error sending create application transaction: {result.stderr}")


def configure_appgate_server():
    application_key_name = st.session_state["application_key_name"]
    appgate_server_url = st.session_state.get("appgate_server_url", "http://localhost:42169")

    st.subheader("3. Configure the offchain AppGate Server")
    code = f"""query_node_rpc_url: {POCKET_RPC_NODE}
query_node_grpc_url: {POCKET_GRPC_NODE}
signing_key: {application_key_name}
self_signing: true
listening_endpoint: {appgate_server_url}
metrics:
  enabled: true
  addr: :9092
pprof:
  enabled: true
  addr: localhost:6061
"""
    st.code(
        language="yaml",
        body=code,
    )

    if is_localnet():
        if st.button("Write AppGate Server configs to disk") or st.session_state.get(
            "appgate_server_config_file_written", False
        ):
            appgate_server_config_file = write_to_temp_yaml_file(code)
            st.subheader("4. Start the offchain AppGate Server")
            cmd_code = f"{POKTROLLD_BIN_PATH} appgate-server \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config={appgate_server_config_file}"
            st.code(
                language="bash",
                body=cmd_code,
            )
            send_a_curl_request()
            st.session_state["appgate_server_config_file_written"] = True
    else:
        appgate_server_config_file = write_to_temp_yaml_file(code)
        with open(appgate_server_config_file, "r") as file:
            st.download_button(
                label="Download AppGate Server Config File",
                data=file,
                file_name="appgate_server_config.toml",
                mime="text/toml",
            )
            st.subheader("4. Start the offchain AppGate Server")
            cmd_code = f"{POKTROLLD_BIN_PATH} appgate-server \\\n --home {POKTROLLD_HOME} \\\n --keyring-backend=test \\\n --config=PATH_TO_CONFIGS_FILE"
            st.code(cmd_code, language="bash")
            send_a_curl_request()


def send_a_curl_request():
    st.subheader("5. Send a curl request to the AppGate Server")
    service_id = st.session_state["application_service_id"]
    curl_command = f"""curl -X POST \\
-H "Content-Type: application/json" \\
--data '{{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}}' \\
http://localhost:42169/{service_id}"""
    st.code(
        curl_command,
        language="bash",
    )
