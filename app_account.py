import json
import random
import string
import subprocess

import streamlit as st

from faucet import import_faucet_key
from poktrolld import (
    CMD_SHARE_JSON_OUTPUT,
    CMD_SHARED_ARGS_KEYRING,
    CMD_SHARED_ARGS_NODE,
    EXPLORER_URL,
    POCKET_RPC_NODE,
    POKTROLLD_BIN_PATH,
)

FAUCET_NAME = "faucet"


def add_account_tab():
    faucet_key_imported = import_faucet_key()
    if not faucet_key_imported:
        st.error("Faucet key cannot be not imported. Please fix your configurations.")
        return

    generate_addr_section()
    fund_section()
    rename_and_export_section()


def generate_addr_section():
    st.subheader("1. Create a new address")

    # Allow generating a new address
    if st.button("Generate New Address"):
        # Generate a random key name to avoid conflicts in the keyring
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        key_name = f"user_key_{random_suffix}"

        # poktrolld keys add <name> [flags]
        command = (
            [
                POKTROLLD_BIN_PATH,
                "keys",
                "add",
                key_name,
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARE_JSON_OUTPUT
        )
        result = subprocess.run(" ".join(command), capture_output=True, shell=True)

        # Show the results of the newley generated address on success
        if result.returncode == 0:
            key_info = json.loads(result.stdout)
            address = key_info["address"]
            mnemonic = key_info["mnemonic"]

            st.session_state["key_name"] = key_name
            st.session_state["address"] = address
            st.session_state["mnemonic"] = mnemonic

            st.success(f"New address generated!")
        else:
            st.error(f"Error generating address: {result.stderr}")

    # Display the generated address and private key IFF they exist
    if "address" not in st.session_state:
        return

    st.write("**Key Name (public name on your local Keyring):**")
    st.code(st.session_state["key_name"])

    st.write("**Address (on-chain public address):**")
    st.code(st.session_state["address"])

    st.write("**Mnemonic Phrase (secret and private to recover your account):**")
    st.code(st.session_state["mnemonic"])

    st.subheader("2. Import your key to your local machine")
    st.warning("You can skip this if you're in LocalNet mode.")
    st.write("Run the following command and copy-paste the mnemonic above when prompted")
    key_name = st.session_state["key_name"]
    st.code(f"poktrolld keys add {key_name} --recover")


def fund_section():
    if "address" not in st.session_state:
        return

    st.subheader("3. Fund your new address")
    if st.button("Fund"):
        address = st.session_state["address"]

        # Run 'poktrolld tx bank send faucet <addr> <amount> --chain-id ...'
        command = (
            [
                POKTROLLD_BIN_PATH,
                "tx",
                "bank",
                "send",
                FAUCET_NAME,
                address,
                "10000000000upokt",
                "--yes",
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARED_ARGS_NODE
            + CMD_SHARE_JSON_OUTPUT
        )
        result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            tx_response = json.loads(result.stdout)
            tx_hash = tx_response.get("txhash", "N/A")
            st.success(f"Address funding tx successfully sent!")
            st.write(
                f"**Transaction Hash (testnet only)**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})"
            )
            st.write("You can also query it like so:")
            st.code(f"poktrolld query tx --type=hash {tx_hash} --node {POCKET_RPC_NODE} --output json | jq")
            st.write(
                f"**Account Balance (testnet only)**: [poktroll/account/{address[0:5]}...{address[-5:]}]({EXPLORER_URL}/account/{address})"
            )
            st.write("You can also query it like so:")
            st.code(f"poktrolld query bank balances {address} --node {POCKET_RPC_NODE}")
            st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error funding address: {result.stderr}")
            st.error(f"Error funding address: {result.stderr}")


def rename_and_export_section():
    if "address" not in st.session_state:
        return

    st.subheader("4. [Optional] Rename your key to semantically identify it locally")
    new_key_name = st.text_input("New Key Name", st.session_state["key_name"])

    # Allow the users to rename their key
    if st.button("Rename"):
        # poktrolld keys rename <old-name> <new-name> [flags]
        command = (
            [
                POKTROLLD_BIN_PATH,
                "keys",
                "rename",
                st.session_state["key_name"],
                new_key_name,
                "--yes",
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARE_JSON_OUTPUT
        )
        result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            st.success(f"Key renamed to {new_key_name}!")
            st.session_state["key_name"] = new_key_name
        else:
            st.error(f"Error renaming key: {result.stderr}")
