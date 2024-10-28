import tempfile

import streamlit as st

from poktrolld import EXPLORER_URL, POCKET_RPC_NODE, is_localnet


def present_tx_result(tx_hash: str) -> None:
    # TODO: Remove this when we have a local explorer as part of LocalNet
    if not is_localnet():
        st.write(f"**Transaction Hash**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})")
    st.write("You can query the tx like so:")
    st.code(f"poktrolld query \\\n tx --type=hash {tx_hash} \\\n --node {POCKET_RPC_NODE} \\\n --output json | jq")


def write_to_temp_yaml_file(data) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file:
        tmp_file.write(data.encode("utf-8"))  # Write data to the file
        tmp_file_path = tmp_file.name  # Get the path to the file
    return tmp_file_path
