import json
import random
import string
import subprocess

import streamlit as st

from faucet import import_faucet_key
from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_KEYRING, CMD_SHARED_ARGS_NODE, POKTROLLD_PATH

EXPLORER_URL = "https://shannon.testnet.pokt.network/poktroll"
FAUCET_NAME = "faucet"


def add_tab_address():
    st.header("Create a new address")

    # Button to generate a new address
    if st.button("Generate New Address"):
        # Generate a random key name to avoid conflicts in the keyring
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        key_name = f"user_key_{random_suffix}"

        # Run 'poktrolld keys add <name> --output json'
        command = (
            [
                POKTROLLD_PATH,
                "keys",
                "add",
                key_name,
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARE_JSON_OUTPUT
        )
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
            rename_command = (
                [
                    POKTROLLD_PATH,
                    "keys",
                    "rename",
                    st.session_state["key_name"],
                    new_key_name,
                    "--yes",
                ]
                + CMD_SHARED_ARGS_KEYRING
                + +CMD_SHARE_JSON_OUTPUT
            )
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
            + +CMD_SHARE_JSON_OUTPUT
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
