import os
import subprocess

import streamlit as st

# Access the faucet private key
faucet_private_key = st.secrets["faucet"]["private_key"]


# Loads private key into keyring if it is available and not already imported.
# Returns True if the faucet is ready to be used, False otherwise.
def import_faucet_key(poktrolld_path: str) -> bool:
    if not faucet_private_key:
        st.error("Faucet private key secret is is not set. Please verify your configurations!")
        return False

    # Check if the key already exists
    check_command = [
        poktrolld_path,
        "keys",
        "show",
        "faucet",
        "--keyring-backend",
        "test",
        "--home",
        "./",
        "--output",
        "json",
    ]
    check_result = subprocess.run(" ".join(check_command), capture_output=True, text=True, shell=True)

    if check_result.returncode == 0:
        print("Faucet key already imported!")
        return True

    # Import the faucet key
    command = [
        poktrolld_path,
        "keys",
        "import-hex",
        "faucet",
        faucet_private_key,
        "--keyring-backend",
        "test",
        "--home",
        "./",
    ]

    result = subprocess.run(" ".join(command), capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        st.error(f"Error importing faucet key: {result.stderr}. Fix the problem and try again!")
        return False

    print("Faucet key imported successfully!")
    return True
