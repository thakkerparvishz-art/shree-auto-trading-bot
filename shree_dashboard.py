import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone
import requests
import time
import random
import yfinance as yf

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY    = "PKMZNC3C3GPVPO3LE7MIKZDS47"
SECRET_KEY = "GPkmZFqzAiv7fhweXnaG7A6YtnxN1gGt2CFJCAwCojgB"
BASE_URL   = "https://paper-api.alpaca.markets"
HEADERS    = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}
IST        = timezone(timedelta(hours=5, minutes=30))

# ── Symbol Mapping ────────────────────────────────────────────────────────────
SYMBOL_MAP = {
    "BTCUSD": "BTC-USD",
    "XAUUSD": "GC=F",
    "EURUSD": "EURUSD=X",
}

TIMEFRAME_MAP = {
    "5Min":  "5m",
    "15Min": "15m",
    "30Min": "30m",
    "1Hour": "60m",
    "1Day":  "1d",
}

PERIOD_MAP = {
    "5m":  "1d",
    "15m": "5d",
    "30m": "1mo",
    "60m": "1mo",
    "1d":  "1y",
}

# ── Admin ─────────────────────────────────────────────────────────────────────
ADMIN = {"username": "Parvish", "password": "Parvish753210#", "role": "admin"}

# ── 5 Client Accounts ─────────────────────────────────────────────────────────
if "clients" not in st.session_state:
    st.session_state.clients = {
        "client1": {"name": "Client 1", "username": "client1", "password": "Client1@123", "active": True,  "mode": "Paper", "strategy": "Strategy 1", "quantity": 1, "trades": [], "balance": 10000},
        "client2": {"name": "Client 2", "username": "client2", "password": "Client2@123", "active": True,  "mode": "Paper", "strategy": "Strategy 1", "quantity": 1, "trades": [], "balance": 10000},
        "client3": {"name": "Client 3", "username": "client3", "password": "Client3@123", "active": True,  "mode": "Paper", "strategy": "Strategy 1", "quantity": 1, "trades": [], "balance": 10000},
        "client4": {"name": "Client 4", "username": "client4", "password": "Client4@123", "active": False, "mode": "Paper", "strategy": "Strategy 1", "quantity": 1, "trades": [], "balance": 10000},
        "client5": {"name": "Client 5", "username": "client5", "password": "Client5@123", "active": False, "mode": "Paper", "strategy": "Strategy 1", "quantity": 1, "trades": [], "balance": 10000},
    }

STRATEGIES = {
    "Strategy 1": "EMA Crossover",
    "Strategy 2": "Empty Slot",
    "Strategy 3": "Empty Slot",
    "Strategy 4": "Empty Slot",
    "Strategy 5": "Empty Slot",
}

st.set_page_config(page_title="SHREE AUTO TRADING BOT", page_icon="🤖", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 50%, #0a0f1e 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
    .main-title { text-align:center; font-size:42px; font-weight:900; letter-spacing:4px; background:linear-gradient(90deg,#00d4aa,#00a8ff,#7b2ff7); -webkit-background-clip:text; -webkit-text-fill-color:transparent; padding:20px 0 5px 0; text-transform:uppercase; }
    .sub-title { text-align:center; color:#8b949e; font-size:13px; letter-spacing:3px; text-transform:uppercase; margin-bottom:20px; }
    .ticker { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:10px 20px; color:#8b949e; font-size:12px; text-align:center; letter-spacing:2px; margin-bottom:15px; }
    .user-badge  { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:8px; padding:8px 16px; color:#00d4aa; font-size:13px; font-weight:700; letter-spacing:2px; text-align:center; margin-bottom:10px; }
    .admin-badge { background:linear-gradient(135deg,#1a0a3a,#2d1060); border:1px solid #7b2ff7; border-radius:8px; padding:8px 16px; color:#bc8cff; font-size:13px; font-weight:700; letter-spacing:2px; text-align:center; margin-bottom:10px; }
    [data-testid="stMetric"] { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:12px; padding:16px; box-shadow:0 4px 15px rgba(0,0,0,0.3); }
    [data-testid="stMetricLabel"] { color:#8b949e !important; font-size:12px !important; letter-spacing:1px; text-transform:uppercase; }
    [data-testid="stMetricValue"] { color:#e6edf3 !important; font-size:24px !important; font-weight:700 !important; }
    .signal-buy  { background:linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-left:4px solid #2ea043; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#3fb950; letter-spacing:1px; margin:10px 0; }
    .signal-sell { background:linear-gradient(135deg,#2d0f0f,#4a1c1c); border:1px solid #da3633; border-left:4px solid #da3633; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#f85149; letter-spacing:1px; margin:10px 0; }
    .signal-hold { background:linear-gradient(135deg,#1c1a0f,#332d10); border:1px solid #9e6a03; border-left:4px solid #d29922; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#d29922; letter-spacing:1px; margin:10px 0; }
    .client-card-active   { background:linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-radius:12px; padding:15px; margin:5px 0; }
    .client-card-inactive { background:linear-gradient(135deg,#2d0f0f,#4a1c1c); border:1px solid #da3633; border-radius:12px; padding:15px; margin:5px 0; }
    .live-badge  { background:#ff4444; color:white; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
    .paper-badge { background:#0066cc; color:white; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
    .price-card  { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:12px; padding:15px; text-align:center; margin:5px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "logged_in"      not in st.session_state: st.session_state.logged_in      = False
if "role"           not in st.session_state: st.session_state.role           = None
if "current_user"   not in st.session_state: st.session_state.current_user   = None
if "login_attempts" not in st.session_state: st.session_state.login_attempts = 0
if "locked_until"   not in st.session_state: st.session_state.locked_until   = None

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_yf_data(symbol, timeframe):
    try:
        yf_symbol  = SYMBOL_MAP.get(symbol, symbol)
        yf_tf      = TIMEFRAME_MAP.get(timeframe, "15m")
        yf_period  = PERIOD_MAP.get(yf_tf, "5d")
        ticker     = yf.Ticker(yf_symbol)
        df         = ticker.history(period=yf_period, interval=yf_tf)
        if df.empty:
            return pd.DataFrame(), "No data available"
        df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
        df = df[["open","high","low","close","volume"]]
        df["ema9"]  = df["close"].ewm(span=9).mean()
        df["ema21"] = df["close"].ewm(span=21).mean()
        delta = df["close"].diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        df["rsi"] = 100 - (100/(1+gain/loss))
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

@st.cache_data(ttl=30)
def load_account():
    try:
        r  = requests.get(f"{BASE_URL}/v2/account",   headers=HEADERS, timeout=10)
        r2 = requests.get(f"{BASE_URL}/v2/positions",  headers=HEADERS, timeout=10)
        return r.json(), r2.json(), None
    except Exception as e:
        return {}, [], str(e)

@st.cache_data(ttl=60)
def get_live_prices():
    prices = {}
    for name, sym in SYMBOL_MAP.items():
        try:
            ticker = yf.Ticker(sym)
            hist   = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                curr  = hist["Close"].iloc[-1]
                prev  = hist["Close"].iloc[-2] if len(hist) > 1 else curr
                chg   = curr - prev
                chgp  = (chg/prev*100) if prev > 0 else 0
                prices[name] = {"price": curr, "change": chg, "change_pct": chgp}
        except:
            prices[name] = {"price": 0, "change": 0, "change_pct": 0}
    return prices

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">SHREE AUTO TRADING BOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🔐 SECURE LOGIN PORTAL · AUTHORIZED ACCESS ONLY 🔐</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.session_state.locked_until and datetime.now(IST) < st.session_state.locked_until:
            remaining = (st.session_state.locked_until - datetime.now(IST)).seconds
            st.error(f"🔒 Account locked! Try again in {remaining} seconds.")
            st.stop()

        st.markdown('<div style="text-align:center;font-size:28px;font-weight:900;color:#00d4aa;letter-spacing:3px;margin-bottom:20px;">🔐 LOGIN</div>', unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")

        if st.button("🚀 LOGIN", use_container_width=True):
            if username == ADMIN["username"] and password == ADMIN["password"]:
                st.session_state.logged_in    = True
                st.session_state.role         = "admin"
                st.session_state.current_user = "Parvish"
                st.session_state.login_attempts = 0
                st.rerun()
            elif username in st.session_state.clients:
                client = st.session_state.clients[username]
                if not client["active"]:
                    st.error("❌ Your account has been deactivated. Contact Admin.")
                elif client["password"] == password:
                    st.session_state.logged_in    = True
                    st.session_state.role         = "client"
                    st.session_state.current_user = username
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    if st.session_state.login_attempts >= 3:
                        st.session_state.locked_until = datetime.now(IST) + timedelta(minutes=5)
                        st.error("🔒 Too many attempts! Locked for 5 minutes.")
                    else:
                        st.error(f"❌ Wrong password! {3-st.session_state.login_attempts} attempts left.")
            else:
                st.error("❌ Username not found!")

        st.markdown("---")
        st.markdown('<div style="text-align:center;color:#8b949e;font-size:11px;">🔐 SHREE AUTO TRADING BOT · PRIVATE & CONFIDENTIAL</div>', unsafe_allow_html=True)

# ── MAIN APP ──────────────────────────────────────────────────────────────────
else:
    now = datetime.now(IST)
    st.markdown('<div class="main-title">SHREE AUTO TRADING BOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">⚡ LIVE 24/7 · BITCOIN · GOLD · EUR/USD ⚡</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ticker">🕐 {now.strftime("%A, %d %B %Y  |  %H:%M:%S IST")}  |  👤 {st.session_state.current_user.upper()}  |  {"👑 ADMIN" if st.session_state.role == "admin" else "👤 CLIENT"}  |  📡 LIVE DATA</div>', unsafe_allow_html=True)

    # ── Live Price Ticker ─────────────────────────────────────────────────────
    prices = get_live_prices()
    p1, p2, p3 = st.columns(3)
    for col, (sym, data) in zip([p1, p2, p3], prices.items()):
        color = "#2ea043" if data["change"] >= 0 else "#f85149"
        arrow = "▲" if data["change"] >= 0 else "▼"
        label = {"BTCUSD":"₿ BITCOIN","XAUUSD":"🥇 GOLD","EURUSD":"💱 EUR/USD"}.get(sym, sym)
        col.markdown(f"""
        <div class="price-card">
            <div style="color:#8b949e;font-size:11px;letter-spacing:2px;">{label}</div>
            <div style="color:#e6edf3;font-size:22px;font-weight:700;">${data['price']:,.4f}</div>
            <div style="color:{color};font-size:13px;">{arrow} ${data['change']:+,.4f} ({data['change_pct']:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Sidebar
    if st.session_state.role == "admin":
        st.sidebar.markdown('<div class="admin-badge">👑 PARVISH · ADMIN</div>', unsafe_allow_html=True)
    else:
        client_name = st.session_state.clients[st.session_state.current_user]["name"]
        st.sidebar.markdown(f'<div class="user-badge">👤 {client_name.upper()} · CLIENT</div>', unsafe_allow_html=True)

    st.sidebar.markdown("## ⚙️ CONTROLS")
    symbol    = st.sidebar.selectbox("📈 Symbol", ["BTCUSD","XAUUSD","EURUSD"], index=0)
    timeframe = st.sidebar.selectbox("⏱ Timeframe", ["5Min","15Min","30Min","1Hour","1Day"], index=1)
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (60s)", value=False)
    st.sidebar.markdown("---")

    if st.session_state.role == "admin":
        st.sidebar.markdown("## 📱 NAVIGATION")
        page = st.sidebar.radio("", ["📊 Dashboard","🧠 Strategies","📈 Backtest","📋 Trade Report","👥 Client Manager"], label_visibility="collapsed")
    else:
        st.sidebar.markdown("## 📱 NAVIGATION")
        page = st.sidebar.radio("", ["📊 Dashboard","💼 My Trading","📋 My Trade Report"], label_visibility="collapsed")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in    = False
        st.session_state.role         = None
        st.session_state.current_user = None
        st.rerun()

    # Account Cards
    account, positions, acc_err = load_account()
    df, data_err = load_yf_data(symbol, timeframe)

    c1, c2, c3, c4, c5 = st.columns(5)
    if not acc_err:
        cash   = float(account.get("cash", 0))
        equity = float(account.get("equity", 0))
        pnl    = float(account.get("unrealized_pl") or 0)
        buying = float(account.get("buying_power", 0))
        c1.metric("💰 CASH",           f"${cash:,.2f}")
        c2.metric("📊 EQUITY",         f"${equity:,.2f}")
        c3.metric("💹 BUYING POWER",   f"${buying:,.2f}")
        c4.metric("📉 UNREALIZED P&L", f"${pnl:,.2f}", delta=f"{pnl:+.2f}")
        c5.metric("🔓 POSITIONS",      len(positions))
    st.markdown("---")

    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    if page == "📊 Dashboard":
        left, right = st.columns([2,1])
        with left:
            if not df.empty:
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                    row_heights=[0.6,0.2,0.2], vertical_spacing=0.02,
                                    subplot_titles=(f"{symbol} · LIVE PRICE + EMA 9/21","RSI (14)","VOLUME"))
                fig.add_trace(go.Candlestick(x=df.index, open=df["open"], high=df["high"],
                              low=df["low"], close=df["close"], name="Price",
                              increasing_line_color="#2ea043", decreasing_line_color="#f85149"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["ema9"],  name="EMA 9",  line=dict(color="#d29922", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["ema21"], name="EMA 21", line=dict(color="#58a6ff", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["rsi"],   name="RSI",    line=dict(color="#bc8cff", width=1.5)), row=2, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="#f85149", row=2, col=1)
                fig.add_hline(y=30, line_dash="dot", line_color="#2ea043", row=2, col=1)
                colors = ["#2ea043" if c >= o else "#f85149" for c,o in zip(df["close"], df["open"])]
                fig.add_trace(go.Bar(x=df.index, y=df["volume"], name="Volume", marker_color=colors), row=3, col=1)
                fig.update_layout(height=600, paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                                  font=dict(color="#8b949e"), xaxis_rangeslider_visible=False,
                                  legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
                                  margin=dict(l=0,r=0,t=30,b=0))
                fig.update_xaxes(gridcolor="#21262d")
                fig.update_yaxes(gridcolor="#21262d")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ {data_err or 'Loading data...'}")

        with right:
            st.markdown("### 🎯 LIVE SIGNAL")
            if not df.empty and len(df) > 2:
                prev = df.iloc[-2]
                curr = df.iloc[-1]
                if prev["ema9"] < prev["ema21"] and curr["ema9"] > curr["ema21"] and curr["rsi"] < 70:
                    st.markdown(f'<div class="signal-buy">🟢 BUY SIGNAL<br><small>{symbol} · EMA Crossover UP</small></div>', unsafe_allow_html=True)
                elif prev["ema9"] > prev["ema21"] and curr["ema9"] < curr["ema21"] and curr["rsi"] > 30:
                    st.markdown(f'<div class="signal-sell">🔴 SELL SIGNAL<br><small>{symbol} · EMA Crossover DOWN</small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="signal-hold">🟡 HOLD<br><small>{symbol} · No Crossover</small></div>', unsafe_allow_html=True)
                st.markdown("### 📊 LIVE VALUES")
                last = df.iloc[-1]
                st.metric("💰 Price",  f"${last['close']:,.4f}")
                st.metric("📈 EMA 9",  f"${last['ema9']:,.4f}")
                st.metric("📉 EMA 21", f"${last['ema21']:,.4f}")
                st.metric("📊 RSI",    f"{last['rsi']:.1f}")
            else:
                st.info("Loading live data...")

            st.markdown("### 📡 MARKET STATUS")
            st.success("🟢 BITCOIN — 24/7 LIVE")
            st.success("🟢 EUR/USD — 24/7 LIVE")
            st.info("🟡 GOLD — Open 7PM-1:30AM IST")

        st.markdown("---")
        st.markdown("### 🔓 OPEN POSITIONS")
        if positions:
            pdf = pd.DataFrame([{"Symbol":p["symbol"],"Qty":p["qty"],
                                  "Entry $":p["avg_entry_price"],"Current $":p["current_price"],
                                  "P&L $":p["unrealized_pl"]} for p in positions])
            st.dataframe(pdf, use_container_width=True)
        else:
            st.info("No open positions.")

    # ── CLIENT TRADING ────────────────────────────────────────────────────────
    elif page == "💼 My Trading":
        client = st.session_state.clients[st.session_state.current_user]
        st.markdown(f"### 💼 MY TRADING PANEL — {client['name'].upper()}")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚙️ TRADE SETTINGS")
            available = [k for k,v in STRATEGIES.items() if v != "Empty Slot"]
            selected_strategy = st.selectbox("🧠 Select Strategy", available)
            quantity = st.number_input("📦 Trade Quantity", min_value=1, max_value=1000, value=client["quantity"])
            st.markdown("#### 🔄 TRADING MODE")
            mode = st.radio("Select Mode", ["📄 Paper Trading","🔴 Live Trading"],
                            index=0 if client["mode"]=="Paper" else 1)
            if "Live" in mode:
                st.error("⚠️ WARNING: Live Trading uses REAL MONEY!")
            if st.button("💾 SAVE SETTINGS", use_container_width=True):
                st.session_state.clients[st.session_state.current_user]["strategy"] = selected_strategy
                st.session_state.clients[st.session_state.current_user]["quantity"] = quantity
                st.session_state.clients[st.session_state.current_user]["mode"]     = "Live" if "Live" in mode else "Paper"
                st.success("✅ Settings saved!")

        with col2:
            st.markdown("#### 📊 MY ACCOUNT")
            client_trades = client["trades"]
            total_pnl     = sum(t.get("pnl",0) for t in client_trades)
            wins          = len([t for t in client_trades if t.get("pnl",0) > 0])
            total         = len(client_trades)
            win_rate      = (wins/total*100) if total > 0 else 0
            roi           = (total_pnl/client["balance"]*100) if client["balance"] > 0 else 0
            st.metric("💰 Balance",      f"${client['balance']:,.2f}")
            st.metric("📈 Total P&L",    f"${total_pnl:+,.2f}")
            st.metric("📐 ROI",          f"{roi:+.2f}%")
            st.metric("🎯 Win Rate",     f"{win_rate:.1f}%")
            st.metric("📊 Total Trades", total)
            mode_badge = f'<span class="live-badge">🔴 LIVE</span>' if client["mode"]=="Live" else f'<span class="paper-badge">📄 PAPER</span>'
            st.markdown(f"**Mode:** {mode_badge}", unsafe_allow_html=True)

    # ── STRATEGIES ────────────────────────────────────────────────────────────
    elif page == "🧠 Strategies":
        st.markdown("### 🧠 STRATEGY MANAGER — 5 SLOTS")
        st.markdown("---")
        for slot, name in STRATEGIES.items():
            col1, col2 = st.columns([3,1])
            with col1:
                if name != "Empty Slot":
                    st.markdown(f'<div class="client-card-active">✅ <b>{slot}</b> — {name}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="background:#161b22;border:2px dashed #30363d;border-radius:12px;padding:15px;margin:5px 0;">📭 <b>{slot}</b> — Empty · Ready for Pine Script</div>', unsafe_allow_html=True)
            with col2:
                if name != "Empty Slot":
                    st.success("🟢 ACTIVE")
                else:
                    st.info("⬜ EMPTY")
        st.markdown("---")
        st.info("📝 Paste your Pine Script in chat → I will deploy it to an empty slot!")

    # ── BACKTEST ──────────────────────────────────────────────────────────────
    elif page == "📈 Backtest":
        st.markdown("### 📈 STRATEGY BACKTESTER")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1: bt_symbol   = st.selectbox("📈 Symbol", ["BTCUSD","XAUUSD","EURUSD"])
        with col2: bt_period   = st.selectbox("📅 Period", ["1 Month","3 Months","6 Months","1 Year"])
        with col3: bt_strategy = st.selectbox("🧠 Strategy", ["EMA Crossover (Strategy 1)"])
        col4, col5 = st.columns(2)
        with col4: initial_capital = st.number_input("💰 Initial Capital ($)", value=10000, step=1000)
        with col5: risk_per_trade  = st.number_input("⚠️ Risk per Trade (%)", value=1.0, step=0.5)

        if st.button("🚀 RUN BACKTEST", use_container_width=True):
            with st.spinner("Fetching historical data from Yahoo Finance..."):
                period_tf_map = {"1 Month":"1mo","3 Months":"3mo","6 Months":"6mo","1 Year":"1y"}
                yf_sym  = SYMBOL_MAP.get(bt_symbol, bt_symbol)
                ticker  = yf.Ticker(yf_sym)
                df_bt   = ticker.history(period=period_tf_map[bt_period], interval="1h")
                if df_bt.empty:
                    st.error("No historical data!")
                else:
                    df_bt = df_bt.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
                    df_bt["ema9"]  = df_bt["close"].ewm(span=9).mean()
                    df_bt["ema21"] = df_bt["close"].ewm(span=21).mean()
                    delta = df_bt["close"].diff()
                    gain  = delta.clip(lower=0).rolling(14).mean()
                    loss  = (-delta.clip(upper=0)).rolling(14).mean()
                    df_bt["rsi"] = 100-(100/(1+gain/loss))

                    capital=initial_capital; position=0; entry_price=0; entry_time=None; trades=[]; equity=[capital]
                    for i in range(22, len(df_bt)):
                        prev=df_bt.iloc[i-1]; curr=df_bt.iloc[i]
                        if prev["ema9"]<prev["ema21"] and curr["ema9"]>curr["ema21"] and curr["rsi"]<70 and position==0:
                            shares=int((capital*risk_per_trade/100)/curr["close"])
                            if shares>0: position=shares; entry_price=curr["close"]; entry_time=df_bt.index[i]
                        elif prev["ema9"]>prev["ema21"] and curr["ema9"]<curr["ema21"] and curr["rsi"]>30 and position>0:
                            pnl=(curr["close"]-entry_price)*position
                            roi=(pnl/(entry_price*position)*100) if entry_price>0 else 0
                            capital+=pnl
                            trades.append({
                                "Strategy": "EMA Crossover",
                                "Entry Time": str(entry_time)[:16],
                                "Exit Time":  str(df_bt.index[i])[:16],
                                "Entry $":    round(entry_price,4),
                                "Exit $":     round(curr["close"],4),
                                "Shares":     position,
                                "P&L $":      round(pnl,2),
                                "ROI %":      round(roi,2),
                                "Result":     "✅ WIN" if pnl>0 else "❌ LOSS"
                            })
                            position=0; entry_price=0; entry_time=None
                        equity.append(capital)

                    if trades:
                        df_t=pd.DataFrame(trades); total_pnl=capital-initial_capital
                        wins=len([t for t in trades if t["P&L $"]>0]); losses=len(trades)-wins
                        win_rate=wins/len(trades)*100; total_roi=total_pnl/initial_capital*100
                        r1,r2,r3,r4,r5,r6=st.columns(6)
                        r1.metric("💰 Final",f"${capital:,.2f}",delta=f"${total_pnl:+,.2f}")
                        r2.metric("📈 ROI",f"{total_roi:+.2f}%")
                        r3.metric("🎯 Win Rate",f"{win_rate:.1f}%")
                        r4.metric("✅ Wins",wins); r5.metric("❌ Losses",losses); r6.metric("📊 Trades",len(trades))
                        fig_eq=go.Figure()
                        fig_eq.add_trace(go.Scatter(y=equity,mode="lines",line=dict(color="#00d4aa",width=2),fill="tozeroy",fillcolor="rgba(0,212,170,0.1)"))
                        fig_eq.update_layout(height=250,paper_bgcolor="#0d1117",plot_bgcolor="#0d1117",font=dict(color="#8b949e"),margin=dict(l=0,r=0,t=10,b=0),showlegend=False)
                        fig_eq.update_xaxes(gridcolor="#21262d"); fig_eq.update_yaxes(gridcolor="#21262d")
                        st.plotly_chart(fig_eq,use_container_width=True)
                        st.dataframe(df_t.style.format({"Entry $":"{:.4f}","Exit $":"{:.4f}","P&L $":"{:+.2f}","ROI %":"{:+.2f}%"}),use_container_width=True)
                        if win_rate>=50 and total_pnl>0:
                            st.success(f"✅ PROFITABLE! Win Rate:{win_rate:.1f}% | ROI:{total_roi:+.2f}%")
                        else:
                            st.warning(f"⚠️ Needs improvement. Win Rate:{win_rate:.1f}% | ROI:{total_roi:+.2f}%")
                    else:
                        st.warning("No trades generated. Try longer period.")

    # ── TRADE REPORT ──────────────────────────────────────────────────────────
    elif page in ["📋 Trade Report","📋 My Trade Report"]:
        if st.session_state.role == "admin":
            st.markdown("### 📋 ALL CLIENTS TRADE REPORT")
            filter_client = st.selectbox("👥 Filter", ["All"]+list(st.session_state.clients.keys()))
        else:
            st.markdown(f"### 📋 MY TRADE REPORT")
            filter_client = st.session_state.current_user

        sample_trades = [
            {"Client":"client1","Strategy":"EMA Crossover","Symbol":"BTCUSD","Entry Time":"2026-06-20 19:15","Square Off Time":"2026-06-20 21:30","Entry $":65420.50,"Exit $":66100.00,"Qty":1,"P&L $":679.50,"ROI %":1.04,"Mode":"Paper","Result":"✅ WIN"},
            {"Client":"client1","Strategy":"EMA Crossover","Symbol":"EURUSD","Entry Time":"2026-06-21 09:00","Square Off Time":"2026-06-21 11:30","Entry $":1.0842,"Exit $":1.0780,"Qty":1000,"P&L $":-62.00,"ROI %":-0.57,"Mode":"Paper","Result":"❌ LOSS"},
            {"Client":"client2","Strategy":"EMA Crossover","Symbol":"BTCUSD","Entry Time":"2026-06-21 08:00","Square Off Time":"2026-06-21 10:00","Entry $":66200.00,"Exit $":67100.00,"Qty":1,"P&L $":900.00,"ROI %":1.36,"Mode":"Paper","Result":"✅ WIN"},
        ]
        all_trades = sample_trades if filter_client=="All" else [t for t in sample_trades if t["Client"]==filter_client]

        if all_trades:
            total_pnl=sum(t["P&L $"] for t in all_trades); wins=len([t for t in all_trades if t["P&L $"]>0])
            win_rate=(wins/len(all_trades)*100); avg_roi=sum(t["ROI %"] for t in all_trades)/len(all_trades)
            s1,s2,s3,s4,s5,s6=st.columns(6)
            s1.metric("📊 Trades",len(all_trades)); s2.metric("💰 P&L",f"${total_pnl:+,.2f}")
            s3.metric("🎯 Win Rate",f"{win_rate:.1f}%"); s4.metric("✅ Wins",wins)
            s5.metric("❌ Losses",len(all_trades)-wins); s6.metric("📐 Avg ROI",f"{avg_roi:+.2f}%")
            st.markdown("---")
            df_r=pd.DataFrame(all_trades)
            if st.session_state.role=="client": df_r=df_r.drop(columns=["Client"])
            st.dataframe(df_r.style.format({"Entry $":"{:.4f}","Exit $":"{:.4f}","P&L $":"{:+.2f}","ROI %":"{:+.2f}%"}),use_container_width=True)
            fig_pnl=go.Figure()
            fig_pnl.add_trace(go.Bar(x=[t["Entry Time"] for t in all_trades],y=[t["P&L $"] for t in all_trades],
                                      marker_color=["#2ea043" if t["P&L $"]>0 else "#f85149" for t in all_trades]))
            fig_pnl.update_layout(height=250,paper_bgcolor="#0d1117",plot_bgcolor="#0d1117",font=dict(color="#8b949e"),margin=dict(l=0,r=0,t=10,b=0))
            fig_pnl.update_xaxes(gridcolor="#21262d"); fig_pnl.update_yaxes(gridcolor="#21262d")
            st.plotly_chart(fig_pnl,use_container_width=True)

    # ── CLIENT MANAGER ────────────────────────────────────────────────────────
    elif page == "👥 Client Manager":
        st.markdown("### 👥 CLIENT MANAGER — ADMIN ONLY")
        st.markdown("---")
        for cid, client in st.session_state.clients.items():
            col1,col2,col3,col4,col5,col6=st.columns([2,1,1,1,1,1])
            with col1:
                if client["active"]:
                    st.markdown(f'<div class="client-card-active">✅ <b>{client["name"]}</b><br><small>@{client["username"]}</small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="client-card-inactive">❌ <b>{client["name"]}</b><br><small>@{client["username"]} · DEACTIVATED</small></div>', unsafe_allow_html=True)
            with col2: st.markdown(f"**{'🟢 ACTIVE' if client['active'] else '🔴 INACTIVE'}**")
            with col3:
                mode_b=f'<span class="live-badge">🔴 LIVE</span>' if client["mode"]=="Live" else f'<span class="paper-badge">📄 PAPER</span>'
                st.markdown(mode_b, unsafe_allow_html=True)
            with col4: st.markdown(f"**{client['strategy']}**")
            with col5:
                if client["active"]:
                    if st.button(f"🔴 Deactivate", key=f"d_{cid}"):
                        st.session_state.clients[cid]["active"]=False; st.rerun()
                else:
                    if st.button(f"🟢 Activate", key=f"a_{cid}"):
                        st.session_state.clients[cid]["active"]=True; st.rerun()
            with col6:
                if st.button(f"🔑 Reset", key=f"r_{cid}"):
                    st.session_state.clients[cid]["password"]=f"{cid.capitalize()}@123"
                    st.info(f"Reset to: {cid.capitalize()}@123")
            st.markdown("---")

        st.markdown("### ✏️ EDIT CLIENT DETAILS")
        edit_client=st.selectbox("Select Client",list(st.session_state.clients.keys()))
        client_data=st.session_state.clients[edit_client]
        ec1,ec2,ec3=st.columns(3)
        with ec1: new_name=st.text_input("👤 Name",value=client_data["name"])
        with ec2: new_pass=st.text_input("🔒 Password",value=client_data["password"])
        with ec3: new_bal=st.number_input("💰 Balance",value=client_data["balance"],step=1000)
        if st.button("💾 UPDATE CLIENT",use_container_width=True):
            st.session_state.clients[edit_client]["name"]=new_name
            st.session_state.clients[edit_client]["password"]=new_pass
            st.session_state.clients[edit_client]["balance"]=new_bal
            st.success(f"✅ {new_name} updated!")

    if auto_refresh:
        time.sleep(60)
        st.rerun()
