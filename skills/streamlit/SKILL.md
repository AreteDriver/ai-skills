---
name: streamlit
description: Streamlit app patterns for layout, state management, data display, and deployment. Invoke with /streamlit.
---

# Streamlit Development

Act as a senior Python developer specializing in Streamlit applications. You understand session state, layout patterns, caching, database integration, and deploying Streamlit in Docker.

## Core Behaviors

**Always:**
- Use `st.session_state` for persistent state across reruns
- Cache expensive computations with `@st.cache_data` or `@st.cache_resource`
- Use `st.columns()` for responsive layouts
- Keep the main app file thin — extract logic into modules
- Handle empty states gracefully (no data yet, loading, errors)

**Never:**
- Store secrets in code — use `st.secrets` or env vars
- Use global mutable variables (Streamlit reruns the script)
- Forget that every widget interaction reruns the entire script
- Block the main thread with long-running operations
- Nest `st.form` inside another form

## App Structure

```python
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

## Session State Patterns

```python
# Initialize with defaults
def init_state():
    defaults = {
        "page": "home",
        "filters": {},
        "cart": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Callback pattern (avoids rerun timing issues)
def on_filter_change():
    st.session_state.filters["status"] = st.session_state._status_filter

st.selectbox("Status", options, key="_status_filter", on_change=on_filter_change)

# Form submission
with st.form("entry_form"):
    name = st.text_input("Name")
    value = st.number_input("Value", min_value=0)
    submitted = st.form_submit_button("Submit")
    if submitted:
        save_entry(name, value)
        st.success("Saved!")
```

## Caching

```python
# Cache data queries (serializable results, auto-invalidated)
@st.cache_data(ttl=300)  # 5 minute TTL
def load_data(query: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(query, conn)

# Cache resources (DB connections, ML models — not serialized)
@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Clear cache programmatically
if st.button("Refresh"):
    st.cache_data.clear()
    st.rerun()
```

## Layout Patterns

```python
# Metric cards row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", 1234, delta="+12%")
col2.metric("Active", 890, delta="-3%")
col3.metric("Rate", "94%", delta="+1.2%")
col4.metric("Avg Time", "4.2m", delta="-0.5m")

# Sidebar filters
with st.sidebar:
    date_range = st.date_input("Date Range", value=(start, end))
    status = st.multiselect("Status", ["Active", "Pending", "Done"])
    if st.button("Apply Filters"):
        st.session_state.filters = {"date": date_range, "status": status}

# Expandable sections
with st.expander("Advanced Options", expanded=False):
    st.slider("Threshold", 0, 100, 50)

# Tabs for content organization
tab1, tab2 = st.tabs(["Chart", "Data"])
with tab1:
    st.line_chart(df)
with tab2:
    st.dataframe(df, use_container_width=True)
```

## Database Integration

```python
import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_PATH", "data/app.db")

@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_db()
    return pd.read_sql_query(sql, conn, params=params)

def execute(sql: str, params: tuple = ()):
    conn = get_db()
    conn.execute(sql, params)
    conn.commit()
```

## Auto-Refresh (Polling)

```python
import time

# Simple polling with rerun
POLL_INTERVAL = 5  # seconds

if "last_poll" not in st.session_state:
    st.session_state.last_poll = time.time()

if time.time() - st.session_state.last_poll > POLL_INTERVAL:
    st.session_state.last_poll = time.time()
    st.rerun()

# Display dashboard (kiosk/TV mode)
st.markdown("""
<meta http-equiv="refresh" content="600">
""", unsafe_allow_html=True)
```

## Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]
```

```yaml
# .streamlit/config.toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

## When to Use This Skill

- Building Streamlit dashboards or data apps
- Managing session state across reruns
- Optimizing Streamlit performance with caching
- Deploying Streamlit apps in Docker
- Creating tablet or TV display interfaces with Streamlit
