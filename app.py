import json
import os
import random
import string
import subprocess

import streamlit as st

from faucet import import_faucet_key
from poktrolld import download_poktrolld, write_executable_to_disk

# Set your faucet's account name and chain ID
FAUCET_NAME = "faucet"
CHAIN_ID = "poktrolld"
POKTROLLD_PATH = "./poktrolld"
EXPLORER_URL = "https://shannon.testnet.pokt.network/poktroll"

# Load the cached binary
poktrolld_bin = download_poktrolld(POKTROLLD_PATH)
write_executable_to_disk(poktrolld_bin, POKTROLLD_PATH)

st.title("Poktrolld Tx Builder")

# Tabs in the main page
(
    tab_address,
    tab_supplier,
    tab_gateway,
    tab_service,
) = st.tabs(["Get Started", "Create Supplier", "Create Gateway", "Create Service"])

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
                "--output",
                "json",
                "--keyring-backend",
                "test",
                "--home",
                "./",
            ]
            result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)
            print(result)

            if result.returncode == 0:
                key_info = json.loads(result.stdout)
                address = key_info["address"]
                mnemonic = key_info["mnemonic"]

                st.session_state["new_address"] = address
                st.session_state["mnemonic"] = mnemonic

                st.success(f"New address generated! Key name: {key_name}")
            else:
                st.error(f"Error generating address: {result.stderr}")

        # Display the address and private key if they exist
        if "new_address" in st.session_state:
            st.write("**New Address:**")
            st.code(st.session_state["new_address"])

            st.write("**Mnemonic Phrase:**")
            st.code(st.session_state["mnemonic"])

        st.header("Fund your new address")
        # Import the faucet key in order to fund new addresses
        faucet_key_imported = import_faucet_key(POKTROLLD_PATH)

        # Fund button
        if st.button("Fund") and faucet_key_imported:
            if "new_address" in st.session_state:
                address = st.session_state["new_address"]
                # Run 'poktrolld tx bank send faucet <addr> <amount> --chain-id ...'
                fund_command = [
                    POKTROLLD_PATH,
                    "tx",
                    "bank",
                    "send",
                    FAUCET_NAME,
                    st.session_state["new_address"],
                    "10000000000upokt",
                    "--node",
                    "https://testnet-validated-validator-rpc.poktroll.com",
                    "--home",
                    "./",
                    "--yes",
                    "--chain-id",
                    CHAIN_ID,
                    "--keyring-backend",
                    "test",
                    "--output",
                    "json",
                ]
                print(" ".join(fund_command))
                result = subprocess.run(" ".join(fund_command), capture_output=True, text=True, shell=True)

                if result.returncode == 0:
                    tx_response = json.loads(result.stdout)
                    tx_hash = tx_response.get("txhash", "N/A")
                    st.success(
                        f"Address funding tx successfully sent! Transaction Hash: [{tx_hash}]({EXPLORER_URL}/tx/{tx_hash})"
                    )
                    st.write(f"Check the account balance on the [explorer]({EXPLORER_URL}/account/{address}).")
                    st.write("Note that you may need to wait up to 30 seconds for changes to show up.")
                else:
                    st.error(f"Error funding address: {result.stderr}")
            else:
                st.warning("Please generate an address first.")

    with tab_supplier:
        st.header("Create Supplier")
        st.write("This feature is coming soon!")

    with tab_gateway:
        st.header("Create Supplier")
        st.write("This feature is coming soon!")

    with tab_service:
        st.header("Create Service")
        st.write("This feature is coming soon!")
