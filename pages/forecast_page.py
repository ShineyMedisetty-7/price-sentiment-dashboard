# ---- pages/forecast_page.py ----

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from forecast.prophet_model_improved import (
    train_and_tune,
    forecast,
    load_model,
    prepare_df
)
from config import CFG
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np


def render(price_df):
    st.markdown("""
<style>

 /* 🔥 Fix TABLE text visibility in dark mode */
[data-testid="stTable"] td, 
[data-testid="stTable"] th {
    color: #000 !important;
    font-weight: 600 !important;
}

/* 🔥 Fix DATAFRAME text visibility */
.stDataFrame table td, 
.stDataFrame table th {
    color: #000 !important;
    font-weight: 600 !important;
}

/* 🔥 Fix METRIC VALUE (MAE / MSE / RMSE) */
div[data-testid="stMetricValue"] {
    color: #000 !important;
    font-size: 24px !important;
    font-weight: 700 !important;
}

/* 🔥 Fix METRIC LABEL text */
div[data-testid="stMetricLabel"] {
    color: #222 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* 🔥 Fix METRIC DELTA arrow text */
div[data-testid="stMetricDelta"] {
    color: #000 !important;
}

/* OPTIONAL: Make table background lighter for better contrast */
.stDataFrame {
    background-color: #f0f0f0 !important;
}

</style>
""", unsafe_allow_html=True)

    st.subheader(f"📈 Prophet Forecast — Next {CFG.FORECAST_DAYS} Days")

    # -------------------------------------------------------------
    # 1) Load model or train new one
    # -------------------------------------------------------------
    df_raw = price_df.copy()
    df = prepare_df(df_raw)

    try:
        model = load_model()
        st.success("Loaded existing trained model.")
    except FileNotFoundError:
        st.warning("Model not found — training...")
        with st.spinner("Training Prophet model..."):
            model, info = train_and_tune(df_raw, run_grid=False)
        st.success("Model trained & saved!")

    # -------------------------------------------------------------
    # 2) Forecast
    # -------------------------------------------------------------
    st.info(f"Generating forecast for next {CFG.FORECAST_DAYS} days...")
    fc = forecast(model, df_raw, periods=CFG.FORECAST_DAYS)

    if "ds" not in fc.columns:
        st.error("Forecast output missing 'ds' column.")
        return

    last_date = df_raw["date"].max()
    future_mask = fc["ds"] > last_date

    # -------------------------------------------------------------
    # 3) Plot Historical + Forecast
    # -------------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_raw["date"],
        y=df_raw["price"],
        mode="lines",
        name="Historical",
        line=dict(color="#6b7280")
    ))

    fig.add_trace(go.Scatter(
        x=fc.loc[future_mask, "ds"],
        y=fc.loc[future_mask, "yhat"],
        mode="lines+markers",
        name="Forecast",
        line=dict(color="#6d28d9")
    ))

    # Confidence Band
    if future_mask.any():
        dates = fc.loc[future_mask, "ds"]
        upper = fc.loc[future_mask, "yhat_upper"]
        lower = fc.loc[future_mask, "yhat_lower"]

        fig.add_trace(go.Scatter(
            x=pd.concat([dates, dates[::-1]]),
            y=pd.concat([upper, lower[::-1]]),
            fill="toself",
            fillcolor="rgba(124,58,237,0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            name="95% Interval"
        ))

    fig.update_layout(
        title="Historical + Prophet Forecast",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------
    # 4) Forecast Table
    # -------------------------------------------------------------
    upcoming = fc.loc[future_mask, ["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()

    if not upcoming.empty:
        upcoming.rename(columns={
            "ds": "date",
            "yhat": "forecast",
            "yhat_lower": "lower",
            "yhat_upper": "upper"
        }, inplace=True)

        upcoming["date"] = upcoming["date"].dt.date
        upcoming[["forecast", "lower", "upper"]] = upcoming[["forecast", "lower", "upper"]].round(2)

        st.subheader("📄 Forecast Table")
        st.table(upcoming.set_index("date"))
    else:
        st.info("No future forecast found.")

    # -------------------------------------------------------------
    # 5) Compute Performance Metrics
    # -------------------------------------------------------------
    st.subheader("📊 Forecast Performance (In-Sample)")

    # align timestamps
    df_raw2 = df_raw.copy()
    df_raw2["ds"] = pd.to_datetime(df_raw2["date"]).dt.normalize()

    merged = pd.merge(
        df_raw2[["ds", "price"]],
        fc[["ds", "yhat"]],
        on="ds",
        how="inner"
    )

    if merged.empty:
        st.warning("Not enough overlapping rows to compute metrics.")
        return

    eval_days = min(30, len(merged) - 1)
    kpi_df = merged.tail(eval_days)

    mae = mean_absolute_error(kpi_df["price"], kpi_df["yhat"])
    mse = mean_squared_error(kpi_df["price"], kpi_df["yhat"])
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((kpi_df["price"] - kpi_df["yhat"]) / kpi_df["price"])) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MAE", f"{mae:.2f}")
    c2.metric("MSE", f"{mse:.2f}")
    c3.metric("RMSE", f"{rmse:.2f}")
    c4.metric("MAPE (%)", f"{mape:.2f}")

    # -------------------------------------------------------------
    # 6) Prophet Components (Trend, Seasonality)
    # -------------------------------------------------------------
    if st.checkbox("Show Prophet Components"):
        st.subheader("🔎 Prophet Components")

        df_full = prepare_df(price_df)
        future_df = model.make_future_dataframe(periods=CFG.FORECAST_DAYS)

        last = df_full.iloc[-1]
        regressors = ['MA7', 'MA30', 'lag1', 'lag7', 'pct_change', 'volatility_7']

        for r in regressors:
            if r in df_full.columns:
                future_df[r] = last[r]

        fc_full = model.predict(future_df)

        comp_fig = model.plot_components(fc_full)
        st.pyplot(comp_fig)

    # -------------------------------------------------------------
    # 7) Download CSV
    # -------------------------------------------------------------
    csv = fc.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Full Forecast CSV", csv, "forecast.csv", "text/csv")
