import subprocess

import streamlit as st

from poktrolld import CMD_ARGS_JSON, CMD_ARGS_KEYRING, POKTROLLD_BIN_PATH, is_beta_testnet, is_localnet

faucet_secrets = None
if is_localnet():
    faucet_secrets = st.secrets["faucet"]["localnet"]
    print("Loading LocalNet secrets")
elif is_beta_testnet():
    faucet_secrets = st.secrets["faucet"]["beta"]
    print("Loading Beta secrets")
else:
    faucet_secrets = st.secrets["faucet"]["alpha"]
    print("Loading Alpha secrets")

FAUCET_NAME = faucet_secrets["name"]
FAUCET_ADDRESS = faucet_secrets["address"]
FAUCET_PRIVATE_KEY = faucet_secrets["private_key"]
print(f"FAUCET_ADDRESS: {FAUCET_ADDRESS}")
# print(f"FAUCET_PRIVATE_KEY: {FAUCET_PRIVATE_KEY}")


# Loads private key into keyring if it is available and not already imported.
# Returns True if the faucet is ready to be used, False otherwise.
def import_faucet_key() -> bool:
    if not FAUCET_PRIVATE_KEY:
        st.error("Faucet private key secret is is not set. Please verify your configurations!")
        return False
    # Check if the key already exists
    check_command = (
        [
            POKTROLLD_BIN_PATH,
            "keys",
            "show",
            FAUCET_NAME,
        ]
        + CMD_ARGS_KEYRING
        + CMD_ARGS_JSON
    )
    check_result = subprocess.run(" ".join(check_command), capture_output=True, shell=True)
    if check_result.returncode == 0:
        return True

    # Import the faucet key
    command = [
        POKTROLLD_BIN_PATH,
        "keys",
        "import-hex",
        FAUCET_NAME,
        FAUCET_PRIVATE_KEY,
    ] + CMD_ARGS_KEYRING
    result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        st.error(f"Error importing faucet key: {result.stderr}. Fix the problem and try again!")
        return False

    print("Faucet key imported successfully!")
    return True
