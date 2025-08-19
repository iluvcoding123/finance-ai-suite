# overview.py — Manual Portfolio with Share Price input
# test
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finance AI Suite — Overview", layout="wide")
st.title("Finance AI Suite — Overview (Manual Entry)")
st.caption("Add ticker + shares + share price. Pie shows % by market value.")

# --- state ---
if "positions" not in st.session_state:
    # each: {"ticker": str, "shares": float, "price": float}
    st.session_state.positions = []

def _norm(t: str) -> str:
    return (t or "").strip().upper()

def upsert(ticker: str, shares: float, price: float):
    t = _norm(ticker)
    if not t or shares <= 0 or price <= 0:
        return
    for p in st.session_state.positions:
        if p["ticker"] == t:
            p["shares"] = float(shares)
            p["price"] = float(price)
            return
    st.session_state.positions.append({
        "ticker": t,
        "shares": float(shares),
        "price": float(price)
    })

# --- sidebar: add / clear ---
st.sidebar.header("Add / Update Holding")
with st.sidebar.form("add_form", clear_on_submit=True):
    t = st.text_input("Ticker", placeholder="e.g., AAPL")
    s = st.number_input("Shares", min_value=0.0, step=1.0, value=0.0)
    p = st.number_input("Share Price ($)", min_value=0.0, step=1.0, value=0.0)
    if st.form_submit_button("Add / Update"):
        if _norm(t) and s > 0 and p > 0:
            upsert(t, s, p)
        else:
            st.sidebar.warning("Enter ticker, shares > 0, and price > 0.")

st.sidebar.divider()
if st.sidebar.button("Clear portfolio", use_container_width=True):
    st.session_state.positions = []

# --- main: table + pie + remove ---
if not st.session_state.positions:
    st.info("👈 Add tickers, shares, and price in the sidebar to see the pie chart.")
else:
    # always construct dataframe with all needed cols
    df = pd.DataFrame(st.session_state.positions, columns=["ticker", "shares", "price"])
    df["value"] = df["shares"] * df["price"]
    df = (
        df.groupby("ticker", as_index=False)[["shares","price","value"]].sum()
          .sort_values("value", ascending=False)
          .reset_index(drop=True)
    )
    total_value = float(df["value"].sum())
    df["allocation"] = df["value"] / total_value if total_value > 0 else 0.0

    st.subheader("Holdings")
    st.dataframe(
        df.rename(columns={
            "ticker": "Ticker",
            "shares": "Shares",
            "price": "Price ($)",
            "value": "Value ($)",
            "allocation": "Allocation"
        }).style.format({
            "Shares": "{:.4f}",
            "Price ($)": "${:,.2f}",
            "Value ($)": "${:,.2f}",
            "Allocation": "{:.2%}"
        }),
        use_container_width=True,
        height=min(380, 60 + 36 * len(df)),
    )

    if total_value > 0:
        fig = px.pie(df, names="ticker", values="value", title="Portfolio Allocation (by Market Value)")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Manage Holdings")
    to_remove = st.multiselect("Remove tickers", df["ticker"].tolist(), placeholder="Pick one or more…")
    if st.button("Remove selected"):
        if to_remove:
            keep = set(df["ticker"]) - set(to_remove)
            st.session_state.positions = [
                p for p in st.session_state.positions if p["ticker"] in keep
            ]
            st.rerun()
        else:
            st.warning("No tickers selected.")

st.divider()
st.caption("Future step: hook up yfinance so you only type ticker + shares and price auto-fills.")