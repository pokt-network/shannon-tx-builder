import json
import os
import random
import string
import subprocess
import time

import streamlit as st

from faucet import import_faucet_key
from poktrolld import download_poktrolld, is_poktrolld_available, write_executable_to_disk


def add_supplier_tab():
    st.header("Create Supplier")
    st.write("This feature is coming soon!")
