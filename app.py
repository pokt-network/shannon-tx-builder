import time

import streamlit as st

from app_account import add_account_tab
from app_application import add_application_tab
from app_service import add_service_tab
from app_supplier import add_supplier_tab
from poktrolld import POCKET_ENV, download_poktrolld, is_poktrolld_available, write_poktrolld_to_disk

# Download poktrolld binary  (CLI) if it's not available
if not is_poktrolld_available():
    st.warning("poktrolld not available. About to start download...")
    with st.spinner("Downloading poktrolld binary. Please wait..."):
        poktrolld_bin = download_poktrolld()
        is_poktrolld_bin_ready = write_poktrolld_to_disk(poktrolld_bin)
        if not is_poktrolld_bin_ready:
            st.error("Failed to download poktrolld. Please check the logs for more information.")
        time.sleep(1)

# App title
st.title(f"Shannon Tx Builder ({POCKET_ENV.capitalize()})")

# Application Tabs Setup
(
    tab_account,
    tab_service,
    tab_supplier,
    tab_application_gateway,
) = st.tabs(
    [
        "Account - Create & Fund",
        "Service - Create & Commit",
        "Supplier - Stake & Relay Mine",
        "Application & Gateway - Stake & Serve",
    ]
)

# Actual Application Tabs
if not is_poktrolld_available():
    st.error("Failed to download poktrolld. Please check the logs for more information.")
else:
    # Sidebar
    # TODO: This is a WIP to add config exporting + session clearing.
    with st.sidebar:
        st.write(
            """
TODO:\n
- Export all configs\n
- Clear session state
- Faucet only page
- Governance page
- Migrate from AppGateSerer to PATH
- Got ideas? Add them to this list!
"""
        )

    with tab_account:
        add_account_tab()
    with tab_service:
        add_service_tab()
    with tab_supplier:
        add_supplier_tab()
    with tab_application_gateway:
        add_application_tab()
    # TODO: Funding only page - fund an existing account
    # TODO: Governance page - view & update governance params
