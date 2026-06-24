import requests
import math

# =========================================================================
# 4-CONFLUENCE STRATEGY — BTC 15m (Python Version)
# Converted from Pine Script v6
# =========================================================================

# ── Default Parameters (matching your TradingView settings) ──────────────
PARAMS = {
    # 1. Multi-Timeframe RSI
    "rsi_len":    14,
    "rsi_bull":   55,
    "rsi_bear":   45,

    # 2. Support/Resistance + Volume
    "pivot_len":  5,
    "vol_len":    20,
    "vol_mult":   1.35,
    "sr_buffer":  0.006,   # 0.6%

    # 3. Squeeze Momentum
    "bb_len":     20,
    "bb_mult":    2.0,
    "kc_mult":    1.6,

    # 4. WaveTrend
    "wt_channel": 10,
    "wt_average": 21,
    "wt_ob":      55,
    "wt_os":      -55,

    # 5. Risk Management
    "sl_perc":    0.012,   # 1.2%
    "rr_ratio":   3.0,     # 3:1 Risk Reward
    "breakeven":  True,
    "be_trigger": 1.0,     # Move SL to BE after 1R

    # 6. Confluence
    "min_confluence": 2,   # Minimum 2 out of 4

    # 7. ADX Trend Filter
    "use_adx":    True,
    "adx_len":    14,
    "adx_smooth": 14,
    "adx_thresh": 20,
}


def sma(data, length):
    if len(data) < length:
        return [None] * len(data)
    result = [None] * (length - 1)
    for i in range(length - 1, len(data)):
        result.append(sum(data[i-length+1:i+1]) / length)
    return result


def ema(data, length):
    result = [None] * len(data)
    k = 2 / (length + 1)
    for i in range(len(data)):
        if data[i] is None:
            continue
        if result[i-1] is None:
            result[i] = data[i]
        else:
            result[i] = data[i] * k + result[i-1] * (1 - k)
    return result


def rsi(close, length=14):
    result = [None] * len(close)
    gains = []
    losses = []
    for i in range(1, len(close)):
        change = close[i] - close[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    if len(gains) < length:
        return result

    avg_gain = sum(gains[:length]) / length
    avg_loss = sum(losses[:length]) / length

    for i in range(length, len(close)):
        if avg_loss == 0:
            result[i] = 100
        else:
            rs = avg_gain / avg_loss
            result[i] = 100 - (100 / (1 + rs))
        if i < len(gains):
            avg_gain = (avg_gain * (length-1) + gains[i]) / length
            avg_loss = (avg_loss * (length-1) + losses[i]) / length

    return result


def stdev(data, length):
    result = [None] * len(data)
    for i in range(length-1, len(data)):
        window = data[i-length+1:i+1]
        if None in window:
            continue
        mean = sum(window) / length
        variance = sum((x - mean) ** 2 for x in window) / length
        result[i] = math.sqrt(variance)
    return result


def atr(high, low, close, length=14):
    tr = [None]
    for i in range(1, len(close)):
        h, l, pc = high[i], low[i], close[i-1]
        tr.append(max(h-l, abs(h-pc), abs(l-pc)))
    result = [None] * len(close)
    if len(tr) >= length:
        result[length] = sum(tr[1:length+1]) / length
        for i in range(length+1, len(tr)):
            if tr[i] is not None and result[i-1] is not None:
                result[i] = (result[i-1] * (length-1) + tr[i]) / length
    return result


def linreg(data, length):
    result = [None] * len(data)
    for i in range(length-1, len(data)):
        window = data[i-length+1:i+1]
        if None in window:
            continue
        x = list(range(length))
        y = window
        n = length
        sum_x  = sum(x)
        sum_y  = sum(y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        m = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
        b = (sum_y - m*sum_x) / n
        result[i] = m*(length-1) + b
    return result


def pivot_high(high, length):
    result = [None] * len(high)
    for i in range(length, len(high)-length):
        window = high[i-length:i+length+1]
        if high[i] == max(window):
            result[i] = high[i]
    return result


def pivot_low(low, length):
    result = [None] * len(low)
    for i in range(length, len(low)-length):
        window = low[i-length:i+length+1]
        if low[i] == min(window):
            result[i] = low[i]
    return result


def dmi(high, low, close, length=14, smooth=14):
    """Directional Movement Index — returns (DI+, DI-, ADX)"""
    n = len(close)
    di_plus  = [None] * n
    di_minus = [None] * n
    adx      = [None] * n

    dm_plus  = [0.0] * n
    dm_minus = [0.0] * n
    tr_list  = [0.0] * n

    for i in range(1, n):
        up   = high[i]  - high[i-1]
        down = low[i-1] - low[i]
        dm_plus[i]  = up   if up > down and up > 0   else 0
        dm_minus[i] = down if down > up and down > 0 else 0
        tr_list[i]  = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))

    # Smooth
    def wilder_smooth(data, l):
        out = [None] * len(data)
        out[l] = sum(data[1:l+1])
        for i in range(l+1, len(data)):
            out[i] = out[i-1] - out[i-1]/l + data[i]
        return out

    s_tr  = wilder_smooth(tr_list,  length)
    s_dmp = wilder_smooth(dm_plus,  length)
    s_dmm = wilder_smooth(dm_minus, length)

    dx_list = [None] * n
    for i in range(length, n):
        if s_tr[i] and s_tr[i] != 0:
            di_plus[i]  = 100 * s_dmp[i] / s_tr[i]
            di_minus[i] = 100 * s_dmm[i] / s_tr[i]
            total = di_plus[i] + di_minus[i]
            if total != 0:
                dx_list[i] = 100 * abs(di_plus[i] - di_minus[i]) / total

    # ADX = smoothed DX
    valid_dx = [(i, v) for i, v in enumerate(dx_list) if v is not None]
    if len(valid_dx) >= smooth:
        start_idx = valid_dx[smooth-1][0]
        adx[start_idx] = sum(v for _, v in valid_dx[:smooth]) / smooth
        prev_i = start_idx
        for i, v in valid_dx[smooth:]:
            adx[i] = (adx[prev_i] * (smooth-1) + v) / smooth
            prev_i = i

    return di_plus, di_minus, adx


# =========================================================================
# MAIN SIGNAL FUNCTION
# =========================================================================
def generate_confluence_signal(candles_15m, candles_1h=None, candles_4h=None, params=None):
    """
    candles_15m: list of dicts with keys: open, high, low, close, volume
    candles_1h:  list of dicts (optional, for MTF RSI)
    candles_4h:  list of dicts (optional, for MTF RSI)
    Returns: dict with signal, votes, details
    """
    if params is None:
        params = PARAMS

    if len(candles_15m) < 50:
        return {"signal": "HOLD", "bull_votes": 0, "bear_votes": 0, "reason": "Not enough data"}

    # Extract arrays
    close  = [c["close"]  for c in candles_15m]
    high   = [c["high"]   for c in candles_15m]
    low    = [c["low"]    for c in candles_15m]
    volume = [c["volume"] for c in candles_15m]
    hlc3   = [(h+l+c)/3 for h,l,c in zip(high, low, close)]

    # ── 1. MTF RSI ────────────────────────────────────────────────────────
    rsi_15m = rsi(close, params["rsi_len"])
    rsi_cur = rsi_15m[-1] if rsi_15m[-1] else 50

    # Use same TF if HTF not provided
    rsi_1h = rsi_cur
    rsi_4h = rsi_cur
    if candles_1h and len(candles_1h) > params["rsi_len"]:
        c1h = [c["close"] for c in candles_1h]
        r1h = rsi(c1h, params["rsi_len"])
        rsi_1h = r1h[-1] if r1h[-1] else 50
    if candles_4h and len(candles_4h) > params["rsi_len"]:
        c4h = [c["close"] for c in candles_4h]
        r4h = rsi(c4h, params["rsi_len"])
        rsi_4h = r4h[-1] if r4h[-1] else 50

    mtf_bull = rsi_cur > params["rsi_bull"] and rsi_1h > params["rsi_bull"] and rsi_4h > params["rsi_bull"]
    mtf_bear = rsi_cur < params["rsi_bear"] and rsi_1h < params["rsi_bear"] and rsi_4h < params["rsi_bear"]

    # ── 2. Support/Resistance + Volume ────────────────────────────────────
    ph = pivot_high(high, params["pivot_len"])
    pl = pivot_low(low,   params["pivot_len"])

    last_res = next((v for v in reversed(ph) if v is not None), None)
    last_sup = next((v for v in reversed(pl) if v is not None), None)

    vol_sma  = sma(volume, params["vol_len"])
    vol_avg  = vol_sma[-1] if vol_sma[-1] else 1
    vol_spike = volume[-1] > vol_avg * params["vol_mult"]

    cur_close = close[-1]
    buf = params["sr_buffer"]

    near_sup = last_sup and cur_close <= last_sup*(1+buf) and cur_close >= last_sup*(1-buf)
    near_res = last_res and cur_close <= last_res*(1+buf) and cur_close >= last_res*(1-buf)

    sr_bull = near_sup and vol_spike
    sr_bear = near_res and vol_spike

    # ── 3. Squeeze Momentum ───────────────────────────────────────────────
    bb_len  = params["bb_len"]
    bb_mult = params["bb_mult"]
    kc_mult = params["kc_mult"]

    basis   = sma(close, bb_len)
    sd      = stdev(close, bb_len)
    bb_up   = [b+bb_mult*s if b and s else None for b,s in zip(basis, sd)]
    bb_low  = [b-bb_mult*s if b and s else None for b,s in zip(basis, sd)]

    kc_basis = ema(close, bb_len)
    atr_val  = atr(high, low, close, bb_len)
    kc_up    = [k+kc_mult*a if k and a else None for k,a in zip(kc_basis, atr_val)]
    kc_low   = [k-kc_mult*a if k and a else None for k,a in zip(kc_basis, atr_val)]

    squeeze_on = []
    for bu, bl, ku, kl in zip(bb_up, bb_low, kc_up, kc_low):
        if all(v is not None for v in [bu,bl,ku,kl]):
            squeeze_on.append(bl > kl and bu < ku)
        else:
            squeeze_on.append(False)

    # Momentum
    highest  = [max(high[max(0,i-bb_len+1):i+1]) for i in range(len(high))]
    lowest   = [min(low[max(0,i-bb_len+1):i+1])  for i in range(len(low))]
    mid_hl   = [(h+l)/2 for h,l in zip(highest, lowest)]
    mid_bs   = [b if b else c for b,c in zip(basis, close)]
    mom_src  = [c - (mhl+mbs)/2 for c,mhl,mbs in zip(close, mid_hl, mid_bs)]
    mom      = linreg(mom_src, bb_len)

    sqz_bull = mom[-1] is not None and mom[-2] is not None and mom[-1] > 0 and mom[-1] > mom[-2]
    sqz_bear = mom[-1] is not None and mom[-2] is not None and mom[-1] < 0 and mom[-1] < mom[-2]
    sqz_fired_bull = squeeze_on[-2] and not squeeze_on[-1] and mom[-1] and mom[-1] > 0
    sqz_fired_bear = squeeze_on[-2] and not squeeze_on[-1] and mom[-1] and mom[-1] < 0

    sqz_bull_final = sqz_bull or sqz_fired_bull
    sqz_bear_final = sqz_bear or sqz_fired_bear

    # ── 4. WaveTrend ──────────────────────────────────────────────────────
    wt_ch  = params["wt_channel"]
    wt_avg = params["wt_average"]
    wt_ob  = params["wt_ob"]
    wt_os  = params["wt_os"]

    esa   = ema(hlc3, wt_ch)
    d_val = ema([abs(h-e) if e else 0 for h,e in zip(hlc3, esa)], wt_ch)
    ci    = [(h-e)/(0.015*d) if e and d and d!=0 else 0 for h,e,d in zip(hlc3, esa, d_val)]
    wt1   = ema(ci, wt_avg)
    wt2   = sma(wt1, 4)

    wt_cross_up   = wt1[-2] is not None and wt2[-2] is not None and wt1[-1] is not None and wt2[-1] is not None
    wt_cross_up   = wt_cross_up and wt1[-2] < wt2[-2] and wt1[-1] > wt2[-1] and wt1[-1] < wt_os + 25
    wt_cross_down = wt1[-2] is not None and wt2[-2] is not None and wt1[-1] is not None and wt2[-1] is not None
    wt_cross_down = wt_cross_down and wt1[-2] > wt2[-2] and wt1[-1] < wt2[-1] and wt1[-1] > wt_ob - 25

    # ── 5. ADX Trend Filter ───────────────────────────────────────────────
    di_plus, di_minus, adx_vals = dmi(high, low, close, params["adx_len"], params["adx_smooth"])
    adx_cur     = adx_vals[-1] if adx_vals[-1] else 0
    is_trending = adx_cur > params["adx_thresh"]
    trend_ok    = is_trending if params["use_adx"] else True

    # ── Confluence Votes ──────────────────────────────────────────────────
    bull_votes = sum([mtf_bull, sr_bull, sqz_bull_final, wt_cross_up])
    bear_votes = sum([mtf_bear, sr_bear, sqz_bear_final, wt_cross_down])

    min_conf = params["min_confluence"]
    long_cond  = bull_votes >= min_conf and trend_ok
    short_cond = bear_votes >= min_conf and trend_ok

    # ── Risk Management ───────────────────────────────────────────────────
    sl_perc  = params["sl_perc"]
    rr_ratio = params["rr_ratio"]

    if long_cond:
        sl_price = cur_close * (1 - sl_perc)
        risk     = cur_close - sl_price
        tp_price = cur_close + risk * rr_ratio
        signal   = "BUY"
    elif short_cond:
        sl_price = cur_close * (1 + sl_perc)
        risk     = sl_price - cur_close
        tp_price = cur_close - risk * rr_ratio
        signal   = "SELL"
    else:
        sl_price = None
        tp_price = None
        signal   = "HOLD"

    return {
        "signal":      signal,
        "bull_votes":  bull_votes,
        "bear_votes":  bear_votes,
        "adx":         round(adx_cur, 2),
        "is_trending": is_trending,
        "rsi_15m":     round(rsi_cur, 2),
        "rsi_1h":      round(rsi_1h, 2),
        "rsi_4h":      round(rsi_4h, 2),
        "entry":       round(cur_close, 4),
        "sl_price":    round(sl_price, 4) if sl_price else None,
        "tp_price":    round(tp_price, 4) if tp_price else None,
        "votes_detail": {
            "MTF RSI":           "✅" if mtf_bull else ("🔴" if mtf_bear else "⬜"),
            "SR + Volume":       "✅" if sr_bull  else ("🔴" if sr_bear  else "⬜"),
            "Squeeze Momentum":  "✅" if sqz_bull_final else ("🔴" if sqz_bear_final else "⬜"),
            "WaveTrend":         "✅" if wt_cross_up   else ("🔴" if wt_cross_down   else "⬜"),
        }
    }
