import streamlit as st

from poktrolld import EXPLORER_URL, POCKET_RPC_NODE, is_localnet


def present_tx_result(tx_hash: str) -> None:
    if not is_localnet():
        st.write(f"**Transaction Hash**: [poktroll/tx/{tx_hash[0:5]}...{tx_hash[-5:]}]({EXPLORER_URL}/tx/{tx_hash})")
    st.write("You can query the tx like so:")
    st.code(f"poktrolld query \\\n tx --type=hash {tx_hash} \\\n --node {POCKET_RPC_NODE} \\\n --output json | jq")
