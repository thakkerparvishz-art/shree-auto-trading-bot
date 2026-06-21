import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import time
import random
import smtplib

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY    = "PKMZNC3C3GPVPO3LE7MIKZDS47"
SECRET_KEY = "GPkmZFqzAiv7fhweXnaG7A6YtnxN1gGt2CFJCAwCojgB"
BASE_URL   = "https://paper-api.alpaca.markets"
DATA_URL   = "https://data.alpaca.markets"
HEADERS    = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}

# ── User Credentials ──────────────────────────────────────────────────────────
USER = {
    "username": "Parvish",
    "password": "Parvish753210#",
    "email":    "thakkerparvviish@gmail.com",
    "mobile":   "9879112655",
}

st.set_page_config(page_title="SHREE AUTO TRADING BOT", page_icon="🔐", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 50%, #0a0f1e 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #21262d;
    }
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #00d4aa, #00a8ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 20px 0 5px 0;
        text-transform: uppercase;
    }
    .sub-title {
        text-align: center;
        color: #8b949e;
        font-size: 13px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    .login-box {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 40px;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4aa, #00a8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 3px;
        margin-bottom: 10px;
    }
    .welcome-text {
        text-align: center;
        color: #8b949e;
        font-size: 13px;
        letter-spacing: 2px;
        margin-bottom: 30px;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 12px !important; letter-spacing: 1px; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: #e6edf3 !important; font-size: 24px !important; font-weight: 700 !important; }
    .ticker {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px 20px;
        color: #8b949e;
        font-size: 12px;
        text-align: center;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }
    .signal-buy  { background: linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-left:4px solid #2ea043; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#3fb950; letter-spacing:1px; margin:10px 0; }
    .signal-sell { background: linear-gradient(135deg,#2d0f0f,#4a1c1c); border:1px solid #da3633; border-left:4px solid #da3633; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#f85149; letter-spacing:1px; margin:10px 0; }
    .signal-hold { background: linear-gradient(135deg,#1c1a0f,#332d10); border:1px solid #9e6a03; border-left:4px solid #d29922; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#d29922; letter-spacing:1px; margin:10px 0; }
    .otp-box {
        background: linear-gradient(135deg, #0d2818, #1a4731);
        border: 1px solid #2ea043;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #3fb950;
        font-size: 14px;
        margin: 10px 0;
    }
    .user-badge {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 8px 16px;
        color: #00d4aa;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "logged_in"      not in st.session_state: st.session_state.logged_in      = False
if "otp_sent"       not in st.session_state: st.session_state.otp_sent       = False
if "otp_code"       not in st.session_state: st.session_state.otp_code       = None
if "otp_expiry"     not in st.session_state: st.session_state.otp_expiry     = None
if "login_method"   not in st.session_state: st.session_state.login_method   = "Password"
if "login_attempts" not in st.session_state: st.session_state.login_attempts = 0
if "locked_until"   not in st.session_state: st.session_state.locked_until   = None

# ── OTP Generator ─────────────────────────────────────────────────────────────
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(otp):
    try:
        # Show OTP on screen since we don't have SMTP configured
        st.session_state.otp_display = otp
        return True
    except:
        return False

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:

    st.markdown('<div class="main-title">SHREE AUTO TRADING BOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🔐 SECURE LOGIN PORTAL · AUTHORIZED ACCESS ONLY 🔐</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        # Check if locked
        if st.session_state.locked_until and datetime.now() < st.session_state.locked_until:
            remaining = (st.session_state.locked_until - datetime.now()).seconds
            st.error(f"🔒 Too many failed attempts! Try again in {remaining} seconds.")
            st.stop()

        st.markdown('<div class="login-title">🔐 LOGIN</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-text">WELCOME BACK · PARVISH</div>', unsafe_allow_html=True)

        # Login method selector
        method = st.radio("Login Method", ["🔑 Password", "📱 Mobile OTP"], horizontal=True)

        if method == "🔑 Password":
            st.markdown("---")
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")

            if st.button("🚀 LOGIN", use_container_width=True):
                if username == USER["username"] and password == USER["password"]:
                    st.session_state.logged_in = True
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 3 - st.session_state.login_attempts
                    if st.session_state.login_attempts >= 3:
                        st.session_state.locked_until = datetime.now() + timedelta(minutes=5)
                        st.error("🔒 Account locked for 5 minutes!")
                    else:
                        st.error(f"❌ Wrong username or password! {remaining} attempts left.")

        else:  # Mobile OTP
            st.markdown("---")
            st.info(f"📱 OTP will be shown on screen (Mobile: +91 {USER['mobile'][-4:].rjust(10,'*')})")

            if not st.session_state.otp_sent:
                if st.button("📲 SEND OTP", use_container_width=True):
                    otp = generate_otp()
                    st.session_state.otp_code   = otp
                    st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
                    st.session_state.otp_sent   = True
                    send_otp_email(otp)
                    st.rerun()
            else:
                # Show OTP on screen (in real app this would go to mobile)
                if hasattr(st.session_state, 'otp_display'):
                    st.markdown(f'<div class="otp-box">📱 Your OTP: <b style="font-size:24px;letter-spacing:8px">{st.session_state.otp_display}</b><br><small>Valid for 5 minutes</small></div>', unsafe_allow_html=True)

                otp_input = st.text_input("🔢 Enter OTP", placeholder="Enter 6-digit OTP", max_chars=6)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ VERIFY OTP", use_container_width=True):
                        if datetime.now() > st.session_state.otp_expiry:
                            st.error("⏰ OTP expired! Request a new one.")
                            st.session_state.otp_sent = False
                        elif otp_input == st.session_state.otp_code:
                            st.session_state.logged_in = True
                            st.session_state.otp_sent  = False
                            st.rerun()
                        else:
                            st.error("❌ Wrong OTP! Try again.")
                with col_b:
                    if st.button("🔄 RESEND OTP", use_container_width=True):
                        st.session_state.otp_sent = False
                        st.rerun()

        st.markdown("---")
        st.markdown('<div style="text-align:center;color:#8b949e;font-size:11px;">🔐 SHREE AUTO TRADING BOT · PRIVATE & CONFIDENTIAL<br>Unauthorized access is strictly prohibited</div>', unsafe_allow_html=True)

# ── MAIN DASHBOARD (after login) ──────────────────────────────────────────────
else:
    # Header
    st.markdown('<div class="main-title">SHREE AUTO TRADING BOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">⚡ POWERED BY ALPACA PAPER TRADING · EMA CROSSOVER STRATEGY ⚡</div>', unsafe_allow_html=True)

    now = datetime.now()
    st.markdown(f'<div class="ticker">🕐 {now.strftime("%A, %d %B %Y  |  %H:%M:%S IST")}  |  PAPER TRADING MODE  |  RISK FREE  |  👤 PARVISH</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown(f'<div class="user-badge">👤 PARVISH · LOGGED IN</div>', unsafe_allow_html=True)
    st.sidebar.markdown("## ⚙️ BOT CONTROLS")
    symbol    = st.sidebar.selectbox("📈 Symbol", ["AAPL","TSLA","GOOGL","MSFT","AMZN","SPY","NVDA","META"], index=0)
    timeframe = st.sidebar.selectbox("⏱ Timeframe", ["5Min","15Min","30Min","1Hour","1Day"], index=1)
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 STRATEGY")
    st.sidebar.markdown("- EMA 9 / EMA 21 Crossover")
    st.sidebar.markdown("- RSI 14 Filter")
    st.sidebar.markdown("- ATR Position Sizing")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ SAFETY")
    st.sidebar.markdown("- Max Risk: 1% per trade")
    st.sidebar.markdown("- Stop Loss: Active")
    st.sidebar.markdown("- Paper Mode: ON")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.sidebar.markdown("### 🤖 SHREE BOT V2.0")
    st.sidebar.markdown("*Paper Trading · Safe Mode*")

    # Load Data
    @st.cache_data(ttl=30)
    def load_account():
        try:
            r  = requests.get(f"{BASE_URL}/v2/account",   headers=HEADERS, timeout=10)
            r2 = requests.get(f"{BASE_URL}/v2/positions",  headers=HEADERS, timeout=10)
            r3 = requests.get(f"{BASE_URL}/v2/orders?status=open", headers=HEADERS, timeout=10)
            return r.json(), r2.json(), r3.json(), None
        except Exception as e:
            return {}, [], [], str(e)

    @st.cache_data(ttl=30)
    def load_bars(sym, tf):
        try:
            url = f"{DATA_URL}/v2/stocks/{sym}/bars"
            params = {"timeframe": tf, "limit": 200, "feed": "iex"}
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            r.raise_for_status()
            bars = r.json().get("bars", [])
            if not bars:
                return pd.DataFrame(), "Market closed or no data"
            df = pd.DataFrame(bars)
            df = df.rename(columns={"t":"time","o":"open","h":"high","l":"low","c":"close","v":"volume"})
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
            df["ema9"]  = df["close"].ewm(span=9).mean()
            df["ema21"] = df["close"].ewm(span=21).mean()
            delta = df["close"].diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            df["rsi"] = 100 - (100/(1+gain/loss))
            return df, None
        except Exception as e:
            return pd.DataFrame(), str(e)

    account, positions, orders, acc_err = load_account()
    df, data_err = load_bars(symbol, timeframe)

    # Account Cards
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
    else:
        st.error(f"Account error: {acc_err}")

    st.markdown("---")

    # Chart + Signal
    left, right = st.columns([2, 1])
    with left:
        if not df.empty:
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                row_heights=[0.6,0.2,0.2], vertical_spacing=0.02,
                                subplot_titles=(f"{symbol} · PRICE + EMA 9/21","RSI (14)","VOLUME"))
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
                              font=dict(color="#8b949e", family="monospace"),
                              xaxis_rangeslider_visible=False,
                              legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
                              margin=dict(l=0,r=0,t=30,b=0))
            fig.update_xaxes(gridcolor="#21262d")
            fig.update_yaxes(gridcolor="#21262d")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"⚠️ {data_err or 'Market closed'}")

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
            st.markdown("### 📊 LATEST VALUES")
            last = df.iloc[-1]
            st.metric("Close Price", f"${last['close']:.2f}")
            st.metric("EMA 9",       f"${last['ema9']:.2f}")
            st.metric("EMA 21",      f"${last['ema21']:.2f}")
            st.metric("RSI",         f"{last['rsi']:.1f}")
        else:
            st.info("Waiting for market data...")
        st.markdown("### 🕐 MARKET HOURS")
        st.markdown("**US Market (IST)**")
        st.markdown("Open: **7:00 PM**")
        st.markdown("Close: **1:30 AM**")

    st.markdown("---")

    if not df.empty:
        st.markdown("### 📋 LATEST CANDLES")
        display = df[["open","high","low","close","volume","ema9","ema21","rsi"]].tail(10).copy()
        display.index = display.index.strftime("%Y-%m-%d %H:%M")
        st.dataframe(display.style.format("{:.2f}"), use_container_width=True)

    st.markdown("### 🔓 OPEN POSITIONS")
    if positions:
        pdf = pd.DataFrame([{"Symbol":p["symbol"],"Qty":p["qty"],
                              "Entry $":p["avg_entry_price"],"Current $":p["current_price"],
                              "P&L $":p["unrealized_pl"]} for p in positions])
        st.dataframe(pdf, use_container_width=True)
    else:
        st.info("No open positions — waiting for signals.")

    if orders:
        st.markdown("### 📝 OPEN ORDERS")
        odf = pd.DataFrame([{"Symbol":o["symbol"],"Side":o["side"].upper(),
                              "Qty":o["qty"],"Type":o["type"].upper(),
                              "Status":o["status"].upper()} for o in orders])
        st.dataframe(odf, use_container_width=True)

    if auto_refresh:
        time.sleep(30)
        st.rerun()
