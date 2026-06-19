# Streamlit Response
## Example Output
```
# app.py — thin entry point
import streamlit as st
from modules.database import get_connection
from modules.metrics import render_metrics
from modules.sidebar import render_sidebar

st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

# Initialize state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.selected_tab = "Overview"

# Sidebar
render_sidebar()

# Main content
tab1, tab2, tab3 = st.tabs(["Overview", "Details", "Settings"])
with tab1:
    render_metrics()
```
