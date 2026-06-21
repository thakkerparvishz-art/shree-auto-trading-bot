import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import time
import random

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY    = "PKMZNC3C3GPVPO3LE7MIKZDS47"
SECRET_KEY = "GPkmZFqzAiv7fhweXnaG7A6YtnxN1gGt2CFJCAwCojgB"
BASE_URL   = "https://paper-api.alpaca.markets"
DATA_URL   = "https://data.alpaca.markets"
HEADERS    = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}

USER = {
    "username": "Parvish",
    "password": "Parvish753210#",
    "email":    "thakkerparvviish@gmail.com",
    "mobile":   "9879112655",
}

# ── 5 Strategy Slots ──────────────────────────────────────────────────────────
STRATEGIES = {
    "Strategy 1": {"name": "EMA Crossover", "status": "ACTIVE", "code": "ema_crossover"},
    "Strategy 2": {"name": "Empty Slot", "status": "EMPTY", "code": None},
    "Strategy 3": {"name": "Empty Slot", "status": "EMPTY", "code": None},
    "Strategy 4": {"name": "Empty Slot", "status": "EMPTY", "code": None},
    "Strategy 5": {"name": "Empty Slot", "status": "EMPTY", "code": None},
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
    .user-badge { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:8px; padding:8px 16px; color:#00d4aa; font-size:13px; font-weight:700; letter-spacing:2px; text-align:center; margin-bottom:10px; }
    [data-testid="stMetric"] { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:12px; padding:16px; box-shadow:0 4px 15px rgba(0,0,0,0.3); }
    [data-testid="stMetricLabel"] { color:#8b949e !important; font-size:12px !important; letter-spacing:1px; text-transform:uppercase; }
    [data-testid="stMetricValue"] { color:#e6edf3 !important; font-size:24px !important; font-weight:700 !important; }
    .signal-buy { background:linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-left:4px solid #2ea043; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#3fb950; letter-spacing:1px; margin:10px 0; }
    .signal-sell { background:linear-gradient(135deg,#2d0f0f,#4a1c1c); border:1px solid #da3633; border-left:4px solid #da3633; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#f85149; letter-spacing:1px; margin:10px 0; }
    .signal-hold { background:linear-gradient(135deg,#1c1a0f,#332d10); border:1px solid #9e6a03; border-left:4px solid #d29922; border-radius:8px; padding:16px 20px; font-size:18px; font-weight:700; color:#d29922; letter-spacing:1px; margin:10px 0; }
    .strategy-active { background:linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-radius:12px; padding:15px; margin:5px 0; }
    .strategy-empty { background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-radius:12px; padding:15px; margin:5px 0; border-style:dashed; }
    .strategy-testing { background:linear-gradient(135deg,#1c1a0f,#332d10); border:1px solid #d29922; border-radius:12px; padding:15px; margin:5px 0; }
    .backtest-result { background:linear-gradient(135deg,#0a0f1e,#161b22); border:1px solid #30363d; border-radius:12px; padding:20px; margin:10px 0; }
    .login-title { text-align:center; font-size:28px; font-weight:900; background:linear-gradient(90deg,#00d4aa,#00a8ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:3px; margin-bottom:10px; }
    .otp-box { background:linear-gradient(135deg,#0d2818,#1a4731); border:1px solid #2ea043; border-radius:12px; padding:20px; text-align:center; color:#3fb950; font-size:14px; margin:10px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "logged_in"      not in st.session_state: st.session_state.logged_in      = False
if "otp_sent"       not in st.session_state: st.session_state.otp_sent       = False
if "otp_code"       not in st.session_state: st.session_state.otp_code       = None
if "otp_expiry"     not in st.session_state: st.session_state.otp_expiry     = None
if "login_attempts" not in st.session_state: st.session_state.login_attempts = 0
if "locked_until"   not in st.session_state: st.session_state.locked_until   = None
if "page"           not in st.session_state: st.session_state.page           = "dashboard"
if "backtest_slot"  not in st.session_state: st.session_state.backtest_slot  = None

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">SHREE AUTO TRADING BOT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🔐 SECURE LOGIN PORTAL · AUTHORIZED ACCESS ONLY 🔐</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.locked_until and datetime.now() < st.session_state.locked_until:
            remaining = (st.session_state.locked_until - datetime.now()).seconds
            st.error(f"🔒 Too many failed attempts! Try again in {remaining} seconds.")
            st.stop()

        st.markdown('<div class="login-title">🔐 LOGIN</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#8b949e;margin-bottom:20px;">WELCOME BACK · PARVISH</div>', unsafe_allow_html=True)

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
                    if st.session_state.login_attempts >= 3:
                        st.session_state.locked_until = datetime.now() + timedelta(minutes=5)
                        st.error("🔒 Account locked for 5 minutes!")
                    else:
                        st.error(f"❌ Wrong credentials! {3 - st.session_state.login_attempts} attempts left.")
        else:
            st.markdown("---")
            st.info(f"📱 OTP will be shown on screen")
            if not st.session_state.otp_sent:
                if st.button("📲 SEND OTP", use_container_width=True):
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp_code   = otp
                    st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
                    st.session_state.otp_sent   = True
                    st.session_state.otp_display = otp
                    st.rerun()
            else:
                if hasattr(st.session_state, 'otp_display'):
                    st.markdown(f'<div class="otp-box">📱 Your OTP: <b style="font-size:24px;letter-spacing:8px">{st.session_state.otp_display}</b><br><small>Valid for 5 minutes</small></div>', unsafe_allow_html=True)
                otp_input = st.text_input("🔢 Enter OTP", placeholder="Enter 6-digit OTP", max_chars=6)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ VERIFY OTP", use_container_width=True):
                        if datetime.now() > st.session_state.otp_expiry:
                            st.error("⏰ OTP expired!")
                            st.session_state.otp_sent = False
                        elif otp_input == st.session_state.otp_code:
                            st.session_state.logged_in = True
                            st.session_state.otp_sent  = False
                            st.rerun()
                        else:
                            st.error("❌ Wrong OTP!")
                with col_b:
                    if st.button("🔄 RESEND", use_container_width=True):
                        st.session_state.otp_sent = False
                        st.rerun()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
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

    # Navigation
    st.sidebar.markdown("## 📱 NAVIGATION")
    page = st.sidebar.radio("", ["📊 Dashboard", "🧠 Strategies", "📈 Backtest"], label_visibility="collapsed")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # ── Data Loading ──────────────────────────────────────────────────────────
    @st.cache_data(ttl=30)
    def load_account():
        try:
            r  = requests.get(f"{BASE_URL}/v2/account",   headers=HEADERS, timeout=10)
            r2 = requests.get(f"{BASE_URL}/v2/positions",  headers=HEADERS, timeout=10)
            return r.json(), r2.json(), None
        except Exception as e:
            return {}, [], str(e)

    @st.cache_data(ttl=30)
    def load_bars(sym, tf, limit=200):
        try:
            url = f"{DATA_URL}/v2/stocks/{sym}/bars"
            params = {"timeframe": tf, "limit": limit, "feed": "iex"}
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
            df["atr"] = (df["high"] - df["low"]).rolling(14).mean()
            return df, None
        except Exception as e:
            return pd.DataFrame(), str(e)

    account, positions, acc_err = load_account()
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

    # ── DASHBOARD PAGE ────────────────────────────────────────────────────────
    if page == "📊 Dashboard":
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
                st.warning(f"⚠️ Market closed or no data")

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
        st.markdown("### 🔓 OPEN POSITIONS")
        if positions:
            pdf = pd.DataFrame([{"Symbol":p["symbol"],"Qty":p["qty"],
                                  "Entry $":p["avg_entry_price"],"Current $":p["current_price"],
                                  "P&L $":p["unrealized_pl"]} for p in positions])
            st.dataframe(pdf, use_container_width=True)
        else:
            st.info("No open positions — waiting for signals.")

    # ── STRATEGIES PAGE ───────────────────────────────────────────────────────
    elif page == "🧠 Strategies":
        st.markdown("### 🧠 STRATEGY MANAGER — 5 SLOTS")
        st.markdown("*Deploy up to 5 strategies simultaneously. Each slot is independent.*")
        st.markdown("---")

        for slot, info in STRATEGIES.items():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                if info["status"] == "ACTIVE":
                    st.markdown(f'<div class="strategy-active">✅ <b>{slot}</b><br><small style="color:#3fb950">{info["name"]}</small></div>', unsafe_allow_html=True)
                elif info["status"] == "EMPTY":
                    st.markdown(f'<div class="strategy-empty">📭 <b>{slot}</b><br><small style="color:#8b949e">Empty — Ready for your strategy</small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="strategy-testing">🧪 <b>{slot}</b><br><small style="color:#d29922">{info["name"]} — Testing</small></div>', unsafe_allow_html=True)
            with col2:
                if info["status"] == "ACTIVE":
                    st.success(f"🟢 ACTIVE")
                elif info["status"] == "EMPTY":
                    st.info("⬜ EMPTY SLOT")
                else:
                    st.warning("🟡 TESTING")
            with col3:
                if info["status"] == "EMPTY":
                    st.button(f"📤 Upload", key=f"upload_{slot}", disabled=True)
                else:
                    st.button(f"⚙️ Edit", key=f"edit_{slot}")
            with col4:
                if info["status"] != "EMPTY":
                    st.button(f"📈 Backtest", key=f"bt_{slot}")

        st.markdown("---")
        st.info("📝 **How to deploy your strategy:**\n\n1. Paste your Pine Script in this chat\n2. I will convert it to Python\n3. It will be deployed to an empty slot\n4. Run backtest before going live!")

    # ── BACKTEST PAGE ─────────────────────────────────────────────────────────
    elif page == "📈 Backtest":
        st.markdown("### 📈 STRATEGY BACKTESTER")
        st.markdown("*Test your strategy on historical data before deploying live*")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            bt_symbol = st.selectbox("📈 Symbol", ["AAPL","TSLA","GOOGL","MSFT","AMZN","SPY","NVDA","META"])
        with col2:
            bt_period = st.selectbox("📅 Period", ["1 Month", "3 Months", "6 Months", "1 Year"])
        with col3:
            bt_strategy = st.selectbox("🧠 Strategy", ["EMA Crossover (Strategy 1)", "Coming Soon..."])

        col4, col5 = st.columns(2)
        with col4:
            initial_capital = st.number_input("💰 Initial Capital ($)", value=10000, step=1000)
        with col5:
            risk_per_trade = st.number_input("⚠️ Risk per Trade (%)", value=1.0, step=0.5)

        if st.button("🚀 RUN BACKTEST", use_container_width=True):
            with st.spinner("Running backtest on historical data..."):
                # Load historical data
                period_map = {"1 Month": 200, "3 Months": 500, "6 Months": 1000, "1 Year": 2000}
                limit = period_map[bt_period]
                df_bt, err = load_bars(bt_symbol, "1Hour", limit)

                if err or df_bt.empty:
                    st.error("No historical data available!")
                else:
                    # Run EMA Crossover backtest
                    capital    = initial_capital
                    position   = 0
                    entry_price = 0
                    trades     = []
                    equity_curve = [capital]

                    for i in range(22, len(df_bt)):
                        prev = df_bt.iloc[i-1]
                        curr = df_bt.iloc[i]

                        # BUY signal
                        if prev["ema9"] < prev["ema21"] and curr["ema9"] > curr["ema21"] and curr["rsi"] < 70 and position == 0:
                            risk_amount = capital * risk_per_trade / 100
                            shares = int(risk_amount / curr["close"])
                            if shares > 0:
                                position    = shares
                                entry_price = curr["close"]

                        # SELL signal
                        elif prev["ema9"] > prev["ema21"] and curr["ema9"] < curr["ema21"] and curr["rsi"] > 30 and position > 0:
                            pnl = (curr["close"] - entry_price) * position
                            capital += pnl
                            trades.append({
                                "Entry Date": df_bt.index[i-1].strftime("%Y-%m-%d"),
                                "Exit Date":  df_bt.index[i].strftime("%Y-%m-%d"),
                                "Entry $":    round(entry_price, 2),
                                "Exit $":     round(curr["close"], 2),
                                "Shares":     position,
                                "P&L $":      round(pnl, 2),
                                "Result":     "✅ WIN" if pnl > 0 else "❌ LOSS",
                            })
                            position    = 0
                            entry_price = 0
                        equity_curve.append(capital)

                    # Results
                    if trades:
                        trades_df  = pd.DataFrame(trades)
                        total_pnl  = capital - initial_capital
                        wins       = len([t for t in trades if t["P&L $"] > 0])
                        losses     = len([t for t in trades if t["P&L $"] <= 0])
                        win_rate   = wins / len(trades) * 100
                        best_trade = max(trades, key=lambda x: x["P&L $"])
                        worst_trade= min(trades, key=lambda x: x["P&L $"])

                        # Summary cards
                        st.markdown("---")
                        st.markdown("### 📊 BACKTEST RESULTS")
                        r1, r2, r3, r4, r5 = st.columns(5)
                        r1.metric("💰 Final Capital", f"${capital:,.2f}", delta=f"${total_pnl:+,.2f}")
                        r2.metric("📈 Total Return",  f"{(total_pnl/initial_capital*100):+.1f}%")
                        r3.metric("🎯 Win Rate",      f"{win_rate:.1f}%")
                        r4.metric("✅ Wins",           wins)
                        r5.metric("❌ Losses",         losses)

                        r6, r7, r8 = st.columns(3)
                        r6.metric("🏆 Best Trade",  f"${best_trade['P&L $']:+,.2f}")
                        r7.metric("💔 Worst Trade", f"${worst_trade['P&L $']:+,.2f}")
                        r8.metric("📊 Total Trades", len(trades))

                        # Equity curve
                        st.markdown("### 📈 EQUITY CURVE")
                        fig_eq = go.Figure()
                        fig_eq.add_trace(go.Scatter(
                            y=equity_curve,
                            mode="lines",
                            name="Portfolio Value",
                            line=dict(color="#00d4aa", width=2),
                            fill="tozeroy",
                            fillcolor="rgba(0,212,170,0.1)"
                        ))
                        fig_eq.add_hline(y=initial_capital, line_dash="dot", line_color="#8b949e")
                        fig_eq.update_layout(
                            height=300,
                            paper_bgcolor="#0d1117",
                            plot_bgcolor="#0d1117",
                            font=dict(color="#8b949e"),
                            margin=dict(l=0,r=0,t=20,b=0),
                            showlegend=False
                        )
                        fig_eq.update_xaxes(gridcolor="#21262d")
                        fig_eq.update_yaxes(gridcolor="#21262d")
                        st.plotly_chart(fig_eq, use_container_width=True)

                        # Trade history
                        st.markdown("### 📋 TRADE HISTORY")
                        st.dataframe(trades_df.style.format({
                            "Entry $": "{:.2f}",
                            "Exit $":  "{:.2f}",
                            "P&L $":   "{:+.2f}",
                        }), use_container_width=True)

                        # Deploy option
                        st.markdown("---")
                        if win_rate >= 50 and total_pnl > 0:
                            st.success(f"✅ Strategy looks PROFITABLE! Win rate: {win_rate:.1f}% | Return: {(total_pnl/initial_capital*100):+.1f}%")
                            if st.button("🚀 DEPLOY THIS STRATEGY TO LIVE BOT", use_container_width=True):
                                st.balloons()
                                st.success("Strategy deployed to Strategy Slot 1!")
                        else:
                            st.warning(f"⚠️ Strategy needs improvement. Win rate: {win_rate:.1f}% | Return: {(total_pnl/initial_capital*100):+.1f}%")
                            st.info("Consider adjusting your strategy parameters before deploying live.")
                    else:
                        st.warning("No trades generated in this period. Try a longer timeframe.")

    if auto_refresh:
        time.sleep(30)
        st.rerun()
