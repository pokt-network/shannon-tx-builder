import json
import random
import string
import subprocess

import streamlit as st

from faucet import FAUCET_NAME, import_faucet_key
from helpers import present_tx_result
from poktrolld import (
    CMD_SHARE_JSON_OUTPUT,
    CMD_SHARED_ARGS_KEYRING,
    CMD_SHARED_ARGS_NODE,
    EXPLORER_URL,
    POCKET_RPC_NODE,
    POKTROLLD_BIN_PATH,
    POKTROLLD_HOME,
    is_localnet,
)


def add_account_tab():
    faucet_key_imported = import_faucet_key()
    if not faucet_key_imported:
        st.error("Faucet key cannot be not imported. Please fix your configurations.")
        return

    st.header("Create & Fund a new Account")

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
        cmd_keys_add = (
            [
                POKTROLLD_BIN_PATH,
                "keys",
                "add",
                key_name,
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARE_JSON_OUTPUT
        )
        result = subprocess.run(" ".join(cmd_keys_add), capture_output=True, shell=True)

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
    if not was_account_created():
        return

    key_name = st.session_state["key_name"]
    st.write("**Key Name (public name on your local Keyring):**")
    st.code(key_name)

    st.write("**Address (on-chain public address):**")
    st.code(st.session_state["address"])

    st.write("**Mnemonic Phrase (secret and private to recover your account):**")
    st.code(st.session_state["mnemonic"])

    if is_localnet():
        st.subheader("2. Verify the account is in your local keyring for your LocalNet")
        st.write("You can verify the account was generated correctly by running the following command:")

        st.code(f"poktrolld keys show {key_name} \\\n --home {POKTROLLD_HOME}")
    else:
        st.subheader("2. Import your key to your local machine")
        st.write("Run the following command and copy-paste the mnemonic above when prompted")

        st.code(f"poktrolld keys add {key_name} --recover")


def fund_section():
    if not was_account_created():
        return

    st.subheader("3. Fund your new address")
    if st.button("Fund"):
        address = st.session_state["address"]

        # Run 'poktrolld tx bank send faucet <addr> <amount> --chain-id ...'
        cmd_tx_bank_send = (
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
        result = subprocess.run(" ".join(cmd_tx_bank_send), capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            tx_response = json.loads(result.stdout)
            tx_hash = tx_response.get("txhash", "N/A")
            st.success(f"Address funding tx successfully sent!")
            present_tx_result(tx_hash)

            # TODO: Remove this when we have a local explorer as part of LocalNet
            if not is_localnet():
                st.write(
                    f"**Account Balance**: [poktroll/account/{address[0:5]}...{address[-5:]}]({EXPLORER_URL}/account/{address})"
                )
            st.write("You can also query the balance like so:")
            st.code(f"poktrolld query bank balances {address} \\\n --node {POCKET_RPC_NODE} --output json | jq")

            # TODO: Configure this number once we query the block time from on-chain
            st.warning("Note that you may need to wait up to **60 seconds** for changes to show up.")
        else:
            st.error(f"Error funding address: {result.stderr}")
            st.error(f"Error funding address: {result.stderr}")


def rename_and_export_section():
    if not was_account_created():
        return

    st.subheader("4. [Optional] Rename your key to semantically identify it locally")
    st.warning("This is optional and only affects your local keyring.")

    old_key_name = st.session_state["key_name"]
    new_key_name = st.text_input("New Key Name", old_key_name)

    # Allow the users to rename their key
    disabled = old_key_name == new_key_name
    if st.button("Rename", disabled=disabled):
        # poktrolld keys rename <old-name> <new-name> [flags]
        cmd_keys_rename = (
            [
                POKTROLLD_BIN_PATH,
                "keys",
                "rename",
                old_key_name,
                new_key_name,
                "--yes",
            ]
            + CMD_SHARED_ARGS_KEYRING
            + CMD_SHARE_JSON_OUTPUT
        )
        result = subprocess.run(" ".join(cmd_keys_rename), capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            st.success(f"Key renamed from {old_key_name}to {new_key_name}!")
            st.session_state["key_name"] = new_key_name
        else:
            st.error(f"Error renaming key: {result.stderr}")


def was_account_created():
    return "address" in st.session_state
