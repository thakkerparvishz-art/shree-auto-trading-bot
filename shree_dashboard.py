import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time

# --- Config ---
API_KEY    = "PKMNZNC3C3GPVP03LE7MIKZDS47"
SECRET_KEY = "GPkaZFqzAiv7fhwmXnaG7A6YtnxNIgGt2CFJCAwCoJgR"
BASE_URL   = "https://paper-api.alpaca.markets"
HEADERS    = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}

st.set_page_config(page_title="SHREE AUTO TRADING BOT", page_icon="🤖", layout="wide")

st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
.metric-card { background: #1e2130; border-radius: 10px; padding: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 SHREE AUTO TRADING BOT")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "Parvish" and p == "Parvish753210#":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong credentials!")
    st.stop()

# --- Main Dashboard ---
st.title("🤖 SHREE AUTO TRADING BOT")
st.caption(f"Live • {datetime.now().strftime('%d %b %Y %H:%M:%S')}")

def get_account():
    try:
        r = requests.get(f"{BASE_URL}/v2/account", headers=HEADERS, timeout=10)
        return r.json()
    except:
        return {}

def get_positions():
    try:
        r = requests.get(f"{BASE_URL}/v2/positions", headers=HEADERS, timeout=10)
        return r.json()
    except:
        return []

def get_orders():
    try:
        r = requests.get(f"{BASE_URL}/v2/orders?limit=10", headers=HEADERS, timeout=10)
        return r.json()
    except:
        return []

acc = get_account()
positions = get_positions()
orders = get_orders()

# --- Metrics ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    equity = float(acc.get("equity", 0))
    st.metric("💰 Equity", f"${equity:,.2f}")
with col2:
    cash = float(acc.get("cash", 0))
    st.metric("💵 Cash", f"${cash:,.2f}")
with col3:
    pl = float(acc.get("unrealized_pl", 0) or 0)
    st.metric("📈 Unrealized P&L", f"${pl:,.2f}", delta=f"${pl:,.2f}")
with col4:
    buying_power = float(acc.get("buying_power", 0))
    st.metric("⚡ Buying Power", f"${buying_power:,.2f}")

st.divider()

# --- Positions ---
st.subheader("📊 Open Positions")
if positions and isinstance(positions, list):
    df = pd.DataFrame([{
        "Symbol": p.get("symbol"),
        "Qty": p.get("qty"),
        "Entry Price": f"${float(p.get('avg_entry_price',0)):.2f}",
        "Current Price": f"${float(p.get('current_price',0)):.2f}",
        "P&L": f"${float(p.get('unrealized_pl',0)):.2f}",
        "P&L %": f"{float(p.get('unrealized_plpc',0))*100:.2f}%"
    } for p in positions])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No open positions")

st.divider()

# --- Place Order ---
st.subheader("🛒 Place Order")
col1, col2, col3, col4 = st.columns(4)
with col1:
    symbol = st.text_input("Symbol", value="AAPL").upper()
with col2:
    qty = st.number_input("Quantity", min_value=1, value=1)
with col3:
    side = st.selectbox("Side", ["buy", "sell"])
with col4:
    order_type = st.selectbox("Type", ["market", "limit"])

if order_type == "limit":
    limit_price = st.number_input("Limit Price", min_value=0.01, value=100.0)

if st.button(f"🚀 Place {side.upper()} Order", type="primary"):
    order_data = {
        "symbol": symbol,
        "qty": str(qty),
        "side": side,
        "type": order_type,
        "time_in_force": "gtc"
    }
    if order_type == "limit":
        order_data["limit_price"] = str(limit_price)
    try:
        r = requests.post(f"{BASE_URL}/v2/orders", json=order_data, headers=HEADERS, timeout=10)
        if r.status_code in [200, 201]:
            st.success(f"✅ Order placed! {side.upper()} {qty} {symbol}")
        else:
            st.error(f"❌ Error: {r.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ {e}")

st.divider()

# --- Recent Orders ---
st.subheader("📋 Recent Orders")
if orders and isinstance(orders, list):
    df2 = pd.DataFrame([{
        "Symbol": o.get("symbol"),
        "Side": o.get("side","").upper(),
        "Qty": o.get("qty"),
        "Type": o.get("type"),
        "Status": o.get("status"),
        "Time": o.get("created_at","")[:16]
    } for o in orders])
    st.dataframe(df2, use_container_width=True)
else:
    st.info("No recent orders")

if st.button("🔄 Refresh"):
    st.rerun()

if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()
