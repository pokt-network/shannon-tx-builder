import os
import time

import streamlit as st

from app_address import add_tab_address
from app_service import add_tab_service
from app_supplier import add_supplier_tab
from poktrolld import POKTROLLD_PATH, download_poktrolld, is_poktrolld_available, write_executable_to_disk

# Load the cached binary
if not is_poktrolld_available(POKTROLLD_PATH):
    st.warning("Downloading poktrolld binary. Please wait...")
    with st.spinner("Preparing poktrolld binary. Please wait..."):
        poktrolld_bin = download_poktrolld(POKTROLLD_PATH)
        poktrolld_bin_ready = write_executable_to_disk(poktrolld_bin, POKTROLLD_PATH)
        if not poktrolld_bin_ready:
            st.error("Failed to download poktrolld. Please check the logs for more information.")
        time.sleep(1)

st.title("Poktrolld Tx Builder")

# Tabs in the main page
(
    tab_address,
    tab_service,
    tab_supplier,
) = st.tabs(["Get Started", "Create Service", "Create Supplier"])
# (
#     tab_service,
#     tab_address,
#     tab_supplier,
# ) = st.tabs(["Create Service", "Get Started", "Create Supplier"])

if not os.path.exists(POKTROLLD_PATH):
    st.error("Failed to download poktrolld. Please check the logs for more information.")
else:
    with tab_address:
        add_tab_address()
    with tab_service:
        add_tab_service()
    with tab_supplier:
        add_supplier_tab()
