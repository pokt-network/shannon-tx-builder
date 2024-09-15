import os
import platform
import subprocess

import gdown
import requests
import streamlit as st
from requests.exceptions import RequestException

# amd64: https://drive.google.com/file/d/1jFnvP931nh5cX-gq7PnJxUOAQPwCpb_m/view?usp=sharing
# arm64: https://drive.google.com/file/d/1BBBdDHw4e5w8abmAoTKou_dIfDkV4pKD/view?usp=sharing


@st.cache_resource
def download_poktrolld(destination: str) -> bytes:
    if platform.system() == "Darwin":
        file_id = "1ey1lUHyVf2-eF9QZku6uZVJmD6Q0E93E"  # macos arm64
    else:
        # file_id = "1BBBdDHw4e5w8abmAoTKou_dIfDkV4pKD"  # linux arm64
        file_id = "1jFnvP931nh5cX-gq7PnJxUOAQPwCpb_m"  # linux amd64
    url = f"https://drive.google.com/uc?id={file_id}"

    # Check if the binary already exists
    if os.path.exists(destination):
        print("poktrolld binary already exists.")
        return load_executable(destination)

    try:
        print("Downloading poktrolld binary...")
        gdown.download(url, destination, quiet=False)
        os.chmod(destination, 0o755)
        print("poktrolld binary downloaded and ready to use!")
    except RequestException as e:
        st.error(f"An error occurred while downloading poktrolld: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

    return load_executable(destination)


# Load a binary executable into memory as bytes
def load_executable(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        binary_data = f.read()  # Load the file into memory as bytes
    return binary_data


# Function to write binary data to disk
def write_executable_to_disk(binary_data: str, output_path: str) -> None:
    with open(output_path, "wb") as f:
        f.write(binary_data)  # Write the binary data to a new file
    try:
        # Run the chmod +x command to make the file executable
        subprocess.run(["chmod", "+x", output_path], check=True)
        print(f"{output_path} is now executable.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
