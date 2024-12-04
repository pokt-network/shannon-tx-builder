import os
import platform
import subprocess
import sys
import tarfile
from pathlib import Path

import requests
import streamlit as st
import toml
from requests.exceptions import RequestException

# Environment configs
POCKET_ENV = os.getenv("POCKET_ENV", "beta")
if POCKET_ENV == "alpha":
    config_page = ".streamlit/config.alpha.toml"
elif POCKET_ENV == "beta":
    config_page = ".streamlit/config.beta.toml"
elif POCKET_ENV == "localnet":
    config_page = ".streamlit/config.localnet.toml"
else:
    raise Exception(f"POCKET_ENV is not set or does not exist! {POCKET_ENV}")


# Environment helpers
def is_localnet() -> bool:
    return POCKET_ENV == "localnet"


def is_beta_testnet() -> bool:
    return POCKET_ENV == "beta"


# Chain configs
configs = toml.loads(Path(config_page).read_text(encoding="utf-8"))["pocket"]
CHAIN_ID = configs["chain_id"]
EXPLORER_URL = configs["explorer_url"]
RPC_NODE = configs["rpc_node"]
GRPC_NODE = configs["grpc_node"]
POKTROLLD_HOME = configs["poktrolld_home"]
if len(POKTROLLD_HOME) == 0 or not os.path.exists(POKTROLLD_HOME):
    raise Exception("POKTROLLD_HOME is not set or does not exist!")

# poktrolld flag configurations
POKTROLLD_BIN_PATH = "./poktrolld"
CMD_ARGS_JSON = ["--output", "json"]
CMD_ARGS_NODE = [
    "--node",
    RPC_NODE,
    "--chain-id",
    CHAIN_ID,
]
CMD_ARGS_KEYRING = ["--home", POKTROLLD_HOME, "--keyring-backend", "test"]
CMD_ARG_FEES = ["--fees", "1upokt"]


def get_architecture():
    """Determine the platform and architecture."""
    system = platform.system().lower()  # 'linux', 'darwin', etc.
    machine = platform.machine().lower()  # 'x86_64', 'arm64', etc.

    if system not in ["linux", "darwin"]:
        print(f"Unsupported OS: {system}")
        sys.exit(1)

    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        print(f"Unsupported architecture: {machine}")
        sys.exit(1)

    return f"{system}_{arch}"


def get_latest_release_url(arch):
    """Fetch the latest release from GitHub and find the matching asset URL."""
    url = "https://api.github.com/repos/pokt-network/poktroll/releases/latest"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch latest release: {response.status_code}")
        sys.exit(1)

    assets = response.json().get("assets", [])
    for asset in assets:
        if f"poktroll_{arch}.tar.gz" in asset["browser_download_url"]:
            return asset["browser_download_url"]

    print(f"No matching release found for {arch}")
    sys.exit(1)


def download_file(url, filename):
    """Download the file from the given URL."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Failed to download file: {response.status_code}")
        sys.exit(1)


def extract_tarball(filename):
    """Extract the tar.gz file."""
    if tarfile.is_tarfile(filename):
        with tarfile.open(filename) as tar:
            tar.extractall()
            print(f"Extracted {filename} successfully.")
    else:
        print(f"{filename} is not a valid tar file.")
        sys.exit(1)


# Cache poktrolld binary into memory so it's available across different Streamlit sessions
@st.cache_resource
def download_poktrolld() -> bytes:

    # Check if the binary already exists and return if it is
    if is_poktrolld_available():
        print("Loading cached poktrolld")
        return load_poktrolld()

    # Download the binary from GitHub
    try:
        arch = get_architecture()
        print(f"Detected architecture: {arch}")

        url = get_latest_release_url(arch)
        print(f"Downloading from: {url}")

        tarball_filename = url.split("/")[-1]
        download_file(url, tarball_filename)

        extract_tarball(tarball_filename)
        os.remove(tarball_filename)  # Remove the tarball after extraction

        if not is_poktrolld_available():
            raise Exception("poktrolld binary not found after extraction")

        os.chmod(POKTROLLD_BIN_PATH, 0o755)  # Expecting
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
