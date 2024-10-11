import os
import platform
import subprocess

import gdown
import streamlit as st
from requests.exceptions import RequestException

# Chain configs
CHAIN_ID = "poktroll"

# Ecosystem Configs
EXPLORER_URL = "https://shannon.testnet.pokt.network/poktroll"

# Environment configs
POCKET_ENV = os.getenv("POCKET_ENV", "testnet")
POCKET_RPC_NODE_TESTNET = "https://testnet-validated-validator-rpc.poktroll.com"
POCKET_RPC_NODE_LOCALNET = "tcp://127.0.0.1:26657"
POCKET_RPC_NODE = POCKET_RPC_NODE_LOCALNET if POCKET_ENV == "localnet" else POCKET_RPC_NODE_TESTNET

# Account source configs
POKTROLLD_HOME = os.getenv("POKTROLLD_HOME", "./")
if len(POKTROLLD_HOME) == 0 or not os.path.exists(POKTROLLD_HOME):
    raise Exception("POKTROLLD_HOME is not set or does not exist!")

# Binary command configs
POKTROLLD_BIN_PATH = "./poktrolld"
CMD_SHARE_JSON_OUTPUT = ["--output", "json"]
CMD_SHARED_ARGS_NODE = [
    "--node",
    POCKET_RPC_NODE,
    "--chain-id",
    CHAIN_ID,
]
CMD_SHARED_ARGS_KEYRING = ["--home", POKTROLLD_HOME, "--keyring-backend", "test"]


def is_localnet() -> bool:
    return POCKET_ENV == "localnet"


# Cache poktrolld binary into memory so it's available across different Streamlit sessions
@st.cache_resource
def download_poktrolld() -> bytes:
    if platform.system() == "Darwin":
        file_id = "1ey1lUHyVf2-eF9QZku6uZVJmD6Q0E93E"  # macos arm64
    else:
        file_id = "1jFnvP931nh5cX-gq7PnJxUOAQPwCpb_m"  # linux amd64
    url = f"https://drive.google.com/uc?id={file_id}"

    # Check if the binary already exists
    if is_poktrolld_available():
        return load_poktrolld()

    try:
        print("Downloading poktrolld binary...")
        gdown.download(url, POKTROLLD_BIN_PATH, quiet=False)
        os.chmod(POKTROLLD_BIN_PATH, 0o755)
        print("poktrolld binary downloaded and ready to use!")
    except RequestException as e:
        st.error(f"An error occurred while downloading poktrolld: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

    return load_poktrolld()


# Load a binary executable into memory as bytes
def load_poktrolld() -> bytes:
    with open(POKTROLLD_BIN_PATH, "rb") as f:
        binary_data = f.read()  # Load the file into memory as bytes
    return binary_data


# Function to write binary data to disk
def write_poktrolld_to_disk(binary_data: str) -> bool:
    with open(POKTROLLD_BIN_PATH, "wb") as f:
        f.write(binary_data)  # Write the binary data to a new file
    try:
        # Run the chmod +x command to make the file executable
        subprocess.run(["chmod", "+x", POKTROLLD_BIN_PATH], check=True)
        print(f"{POKTROLLD_BIN_PATH} is now executable.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


# Check if the poktrolld binary is available on disk
def is_poktrolld_available() -> bool:
    return os.path.exists(POKTROLLD_BIN_PATH)
