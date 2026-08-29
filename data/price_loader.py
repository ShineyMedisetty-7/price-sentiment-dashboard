# ---- data/price_loader.py ----
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from config import CFG

@st.cache_data(ttl=3600)
# def load_price(file):
#     df = pd.read_csv(file)

#     cols_lower = [c.strip().lower() for c in df.columns]
#     df.columns = cols_lower

#     if "date" not in df.columns or "price" not in df.columns:
#         raise ValueError("CSV must contain 'date' and 'price' columns.")

#     df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
#     df["price"] = pd.to_numeric(df["price"], errors="coerce")
#     df = df.dropna(subset=["date", "price"]).sort_values("date")

#     df = df.drop_duplicates(subset=["date"]).set_index("date")
#     df = df.resample("D").last()
#     df["price"] = df["price"].interpolate().ffill().bfill()
#     return df.reset_index()
# inside data/price_loader.py (update)
def load_price(file):
    df = pd.read_csv(file)
    cols_lower = [c.strip().lower() for c in df.columns]
    df.columns = cols_lower

    if "date" not in df.columns or "price" not in df.columns:
        raise ValueError("CSV must contain 'date' and 'price' columns.")

    # preserve external regressors if present
    external_cols = [c for c in ['competitor_price','discount','sentiment_score'] if c in df.columns]

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["date","price"]).sort_values("date")

    df = df.drop_duplicates(subset=["date"]).set_index("date")
    df = df.resample("D").last()

    # forward/backfill/regressors numeric conversion
    df["price"] = df["price"].interpolate().ffill().bfill()
    for c in external_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df[c] = df[c].interpolate().ffill().bfill()

    return df.reset_index()


def compute_kpis(price_df):
    last = float(price_df["price"].iloc[-1])
    mean_30 = float(price_df["price"].tail(30).mean())
    std_30 = float(price_df["price"].tail(30).std())
    ma_short = float(price_df["price"].tail(CFG.KPIS_WINDOW).mean())

    pct_change = (
        (last - price_df["price"].iloc[-2])
        / price_df["price"].iloc[-2] * 100
        if len(price_df) > 1
        else 0.0
    )

    return {
        "last": last,
        "mean_30": mean_30,
        "volatility_30": std_30,
        "ma_short": ma_short,
        "pct_change_1d": pct_change
    }
