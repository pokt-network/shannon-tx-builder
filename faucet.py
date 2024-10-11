import subprocess

import streamlit as st

from poktrolld import CMD_SHARE_JSON_OUTPUT, CMD_SHARED_ARGS_KEYRING, POKTROLLD_BIN_PATH, is_localnet

FAUCET_NAME = "faucet"


# Loads private key into keyring if it is available and not already imported.
# Returns True if the faucet is ready to be used, False otherwise.
def import_faucet_key() -> bool:
    # Get the faucet private key
    faucet_private_key = (
        st.secrets["faucet"]["localnet"]["private_key"]
        if is_localnet()
        else st.secrets["faucet"]["testnet"]["private_key"]
    )

    if not faucet_private_key:
        st.error("Faucet private key secret is is not set. Please verify your configurations!")
        return False

    # Check if the key already exists
    check_command = (
        [
            POKTROLLD_BIN_PATH,
            "keys",
            "show",
            "faucet",
        ]
        + CMD_SHARED_ARGS_KEYRING
        + CMD_SHARE_JSON_OUTPUT
    )
    check_result = subprocess.run(" ".join(check_command), capture_output=True, shell=True)
    if check_result.returncode == 0:
        return True

    # Import the faucet key
    command = [
        POKTROLLD_BIN_PATH,
        "keys",
        "import-hex",
        "faucet",
        faucet_private_key,
    ] + CMD_SHARED_ARGS_KEYRING
    result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        st.error(f"Error importing faucet key: {result.stderr}. Fix the problem and try again!")
        return False

    print("Faucet key imported successfully!")
    return True
