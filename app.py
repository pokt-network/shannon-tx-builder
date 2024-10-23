import os
import time

import streamlit as st

from app_account import add_account_tab
from app_service import add_service_tab
from app_supplier import add_supplier_tab
from poktrolld import POCKET_ENV, download_poktrolld, is_poktrolld_available, write_poktrolld_to_disk

# Load the cached binary
if not is_poktrolld_available():
    st.warning("Downloading poktrolld binary. Please wait...")
    with st.spinner("Preparing poktrolld binary. Please wait..."):
        poktrolld_bin = download_poktrolld()
        poktrolld_bin_ready = write_poktrolld_to_disk(poktrolld_bin)
        if not poktrolld_bin_ready:
            st.error("Failed to download poktrolld. Please check the logs for more information.")
        time.sleep(1)

# App title
st.title(f"Poktrolld Tx Builder ({POCKET_ENV.capitalize()})")

# Main Tabs
(
    tab_account,
    tab_service,
    tab_supplier,
) = st.tabs(["Account - Create & Fund", "Service - Create & Commit", "Supplier - Stake & Relay Mine"])

# ALl tabs
if not is_poktrolld_available():
    st.error("Failed to download poktrolld. Please check the logs for more information.")
else:

    with st.sidebar:
        st.button("Export all configs")

    with tab_account:
        add_account_tab()
    with tab_service:
        add_service_tab()
    with tab_supplier:
        add_supplier_tab()
