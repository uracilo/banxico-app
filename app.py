import os
import datetime as dt
from datetime import timedelta
from collections import deque

import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="USD Exchange (Banxico)", page_icon="💵", layout="centered")

PRIMARY = "#4F9DDE"
CARD_BG = "rgba(38,39,48,0.75)"
TEXT = "#FAFAFA"
MUTED = "rgba(250,250,250,0.75)"

st.markdown(f"""
<style>
.card {{
  background: {CARD_BG};
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 18px 18px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}}
.card h3 {{
  margin: 0 0 8px 0;
  font-size: 1.05rem;
  color: {MUTED};
  font-weight: 600;
  letter-spacing: .2px;
}}
.value {{
  font-size: 2rem;
  font-weight: 700;
  color: {TEXT};
}}
.list {{
  display: grid;
  grid-template-columns: 1fr auto;
  row-gap: 8px;
  column-gap: 12px;
  margin-top: 6px;
}}
.item-date {{ color: {MUTED}; font-size: .95rem; }}
.item-rate {{ color: {TEXT}; font-weight: 600; font-variant-numeric: tabular-nums; }}
</style>
""", unsafe_allow_html=True)

BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1"
SERIE_USD_MXN_FIX = "SF43718"

TOKEN = st.secrets.get("BANXICO_TOKEN", os.getenv("BANXICO_TOKEN", "")).strip()
if not TOKEN:
    st.error("Banxico token missing. Set it in `.streamlit/secrets.toml` or as env var `BANXICO_TOKEN`.")
    st.stop()

HEADERS = {"Bmx-Token": TOKEN}

LIMITS = {
    "oportuna": {"per_min": 80, "per_day": 40000},
    "historica": {"per_5min": 200, "per_day": 10000},
}

st.session_state.setdefault("rl", {
    "oportuna_min": deque(),
    "oportuna_day": deque(),
    "historica_5min": deque(),
    "historica_day": deque(),
    "day_anchor": dt.date.today(),
})

def purge_old():
    now = dt.datetime.utcnow()
    state = st.session_state.rl
    if state["day_anchor"] != dt.date.today():
        state["oportuna_day"].clear()
        state["historica_day"].clear()
        state["day_anchor"] = dt.date.today()
    one_min_ago = now - timedelta(seconds=60)
    five_min_ago = now - timedelta(seconds=300)
    midnight = dt.datetime.combine(dt.date.today(), dt.time(0, 0))
    for q, window in [("oportuna_min", one_min_ago), ("historica_5min", five_min_ago),
                      ("oportuna_day", midnight), ("historica_day", midnight)]:
        deque_obj = state[q]
        while deque_obj and deque_obj[0] < window:
            deque_obj.popleft()

def record_call(kind: str):
    now = dt.datetime.utcnow()
    state = st.session_state.rl
    if kind == "oportuna":
        state["oportuna_min"].append(now)
        state["oportuna_day"].append(now)
    else:
        state["historica_5min"].append(now)
        state["historica_day"].append(now)

def check_rate_alerts(kind: str):
    purge_old()
    s = st.session_state.rl
    half = 0.5
    warn = 0.75
    day_warn = 0.85
    if kind == "oportuna":
        per_min, per_day = len(s["oportuna_min"]), len(s["oportuna_day"])
        if per_min >= LIMITS[kind]["per_min"] * half:
            st.warning(f"[HALF LIMIT] Oportuna per-minute: {per_min}/{LIMITS[kind]['per_min']}")
        if per_day >= LIMITS[kind]["per_day"] * half:
            st.warning(f"[HALF LIMIT] Oportuna daily: {per_day}/{LIMITS[kind]['per_day']}")
        if per_min >= LIMITS[kind]["per_min"] * warn:
            st.warning(f"Approaching Oportuna per-minute limit!")
        if per_day >= LIMITS[kind]["per_day"] * day_warn:
            st.warning(f"Approaching Oportuna daily limit!")
    else:
        per_5min, per_day = len(s["historica_5min"]), len(s["historica_day"])
        if per_5min >= LIMITS[kind]["per_5min"] * half:
            st.warning(f"[HALF LIMIT] Historica 5-min: {per_5min}/{LIMITS[kind]['per_5min']}")
        if per_day >= LIMITS[kind]["per_day"] * half:
            st.warning(f"[HALF LIMIT] Historica daily: {per_day}/{LIMITS[kind]['per_day']}")
        if per_5min >= LIMITS[kind]["per_5min"] * warn:
            st.warning(f"Approaching Historica 5-min limit!")
        if per_day >= LIMITS[kind]["per_day"] * day_warn:
            st.warning(f"Approaching Historica daily limit!")

@st.cache_data(ttl=120, show_spinner=False)
def fetch_oportuna_fix() -> float:
    url = f"{BASE}/series/{SERIE_USD_MXN_FIX}/datos/oportuno"
    record_call("oportuna")
    check_rate_alerts("oportuna")
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    dato = r.json()["bmx"]["series"][0]["datos"][0]["dato"]
    if dato in (None, "N/E"):
        raise ValueError("No 'oportuno' value available.")
    return float(dato)

@st.cache_data(ttl=600, show_spinner=False)
def fetch_historica_fix(start: dt.date, end: dt.date) -> pd.DataFrame:
    url = f"{BASE}/series/{SERIE_USD_MXN_FIX}/datos/{start.isoformat()}/{end.isoformat()}"
    record_call("historica")
    check_rate_alerts("historica")
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    rows = [
        {"date": pd.to_datetime(d["fecha"], format="%d/%m/%Y", dayfirst=True), "rate": float(d["dato"])}
        for d in r.json()["bmx"]["series"][0].get("datos", [])
        if d.get("dato") and d.get("dato") != "N/E"
    ]
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df

def avg_last_n_points(df: pd.DataFrame, n: int) -> float:
    if df.empty or len(df) < n:
        return float("nan")
    return df.tail(n)["rate"].mean()

try:
    current_rate = fetch_oportuna_fix()
    today = dt.date.today()
    start = today - timedelta(days=120)
    df_all = fetch_historica_fix(start, today)
    avg_15 = avg_last_n_points(df_all, 15)
    avg_30 = avg_last_n_points(df_all, 30)
    df_10 = df_all.tail(10).copy()
    df_10["Date"] = df_10["date"].dt.strftime("%b %d, %Y")
except Exception as e:
    st.error(f"Failed to fetch Banxico data: {e}")
    st.stop()

st.markdown(f"""
<div class="card">
  <h3>1. Current USD Exchange</h3>
  <div class="value">USD → MXN (FIX): {current_rate:,.4f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class="card">
  <h3>2. Average USD Exchange</h3>
  <div class="list">
    <div class="item-date">Last 15 days (avg)</div>
    <div class="item-rate">{(avg_15 if pd.notna(avg_15) else float('nan')):,.4f}</div>
    <div class="item-date">Last month / 30 observations (avg)</div>
    <div class="item-rate">{(avg_30 if pd.notna(avg_30) else float('nan')):,.4f}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

items_html = "\n".join(
    f"""<div class="item-date">{row['Date']}</div><div class="item-rate">{row['rate']:.4f}</div>"""
    for _, row in df_10.iterrows()
)
st.markdown(f"""
<div class="card">
  <h3>3. Past 10 Days USD Exchange</h3>
  <div class="list">
    {items_html}
  </div>
</div>
""", unsafe_allow_html=True)
