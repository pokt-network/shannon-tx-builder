import json
import os
import random
import string
import subprocess
import time

import streamlit as st

from faucet import import_faucet_key
from poktrolld import download_poktrolld, is_poktrolld_available, write_executable_to_disk

# Set your faucet's account name and chain ID
FAUCET_NAME = "faucet"
CHAIN_ID = "poktroll"
POKTROLLD_PATH = "./poktrolld"
EXPLORER_URL = "https://shannon.testnet.pokt.network/poktroll"
CMD_SHARED_ARGS_KEYRING = ["--home", "./", "--keyring-backend", "test", "--output", "json"]
CMD_SHARED_ARGS_NODE = ["--node", "https://testnet-validated-validator-rpc.poktroll.com", "--chain-id", CHAIN_ID]

# Load the cached binary
if not is_poktrolld_available(POKTROLLD_PATH):
    st.warning("Downloading poktrolld binary. Please wait...")
    with st.spinner("Preparing poktrolld binary. Please wait..."):
        poktrolld_bin = download_poktrolld(POKTROLLD_PATH)
        poktrolld_bin_ready = write_executable_to_disk(poktrolld_bin, POKTROLLD_PATH)
        if not poktrolld_bin_ready:
            st.error("Failed to download poktrolld. Please check the logs for more information.")
        time.sleep(1)

st.title("Poktrolld Tx Builder")

# Tabs in the main page
(
    tab_address,
    # tab_supplier,
    # tab_gateway,
    tab_service,
) = st.tabs(["Get Started", "Create Service"])
# ) = st.tabs(["Get Started", "Create Supplier", "Create Gateway", "Create Service"])

if not os.path.exists(POKTROLLD_PATH):
    st.error("Failed to download poktrolld. Please check the logs for more information.")
else:
    with tab_address:
        st.header("Create a new address")

        # Button to generate a new address
        if st.button("Generate New Address"):
            # Generate a random key name to avoid conflicts in the keyring
            random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            key_name = f"user_key_{random_suffix}"

            # Run 'poktrolld keys add <name> --output json'
            command = [
                POKTROLLD_PATH,
                "keys",
                "add",
                key_name,
            ] + CMD_SHARED_ARGS_KEYRING
            result = subprocess.run(" ".join(command), capture_output=True, shell=True)

            if result.returncode == 0:
                key_info = json.loads(result.stdout)
                address = key_info["address"]
                mnemonic = key_info["mnemonic"]

                st.session_state["key_name"] = key_name
                st.session_state["new_address"] = address
                st.session_state["mnemonic"] = mnemonic

                st.success(f"New address generated!")
            else:
                st.error(f"Error generating address: {result.stderr}")

        # Display the address and private key if they exist
        if "new_address" in st.session_state:
            st.write("**Key Name:**")
            st.code(st.session_state["key_name"])

            st.write("**Address:**")
            st.code(st.session_state["new_address"])

            st.write("**Mnemonic Phrase:**")
            st.code(st.session_state["mnemonic"])

            st.subheader("[Optional] Rename your key")

            new_key_name = "Put_your_key_name_here"
            new_key_name = st.text_input("New Key Name", new_key_name)
            if st.button("Rename"):
                rename_command = [
                    POKTROLLD_PATH,
                    "keys",
                    "rename",
                    st.session_state["key_name"],
                    new_key_name,
                    "--yes",
                ] + CMD_SHARED_ARGS_KEYRING
                result = subprocess.run(" ".join(rename_command), capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    st.success(f"Key renamed to {new_key_name}!")
                    st.session_state["key_name"] = new_key_name
                else:
                    st.error(f"Error renaming key: {result.stderr}")

        # Import the faucet key in order to fund new addresses
        faucet_key_imported = import_faucet_key(POKTROLLD_PATH)

        st.header("Fund your new address")

        # Fund button
        if "new_address" not in st.session_state:
            st.warning("Please generate an address first.")
        elif st.button("Fund") and faucet_key_imported:
            address = st.session_state["new_address"]
            # Run 'poktrolld tx bank send faucet <addr> <amount> --chain-id ...'
            fund_command = (
                [
                    POKTROLLD_PATH,
                    "tx",
                    "bank",
                    "send",
                    FAUCET_NAME,
                    st.session_state["new_address"],
                    "10000000000upokt",
                    "--yes",
                ]
                + CMD_SHARED_ARGS_KEYRING
                + CMD_SHARED_ARGS_NODE
            )
            result = subprocess.run(" ".join(fund_command), capture_output=True, text=True, shell=True)

            if result.returncode == 0:
                tx_response = json.loads(result.stdout)
                tx_hash = tx_response.get("txhash", "N/A")
                st.success(f"Address funding tx successfully sent!")
                st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
                st.write(
                    f"**Transaction Hash**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})"
                )
                st.write(
                    f"**Account Balance**: [poktroll/account/{address[0:5]}...{address[-5:]}]({EXPLORER_URL}/account/{address})"
                )
            else:
                st.error(f"Error funding address: {result.stderr}")

    with tab_service:
        st.header("Create Service")
        st.write("This feature is coming soon!")

    # with tab_supplier:
    #     st.header("Create Supplier")
    #     st.write("This feature is coming soon!")

    # with tab_gateway:
    #     st.header("Create Supplier")
    #     st.write("This feature is coming soon!")


def export_key_hex(key_name: str) -> str:
    fund_command = [
        POKTROLLD_PATH,
        "keys",
        "export",
        key_name,
    ] + CMD_SHARED_ARGS_KEYRING
    result = subprocess.run(" ".join(fund_command), capture_output=True, text=True, shell=True)
    # if result.returncode == 0:
