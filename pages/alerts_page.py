# ---- pages/alerts_page.py ----
import streamlit as st
import pandas as pd
from forecast.prophet_model_improved import (
    load_model,
    forecast,
    train_and_tune
)
from config import CFG
from utils.email_utils import send_email_alert


def render(price_df):
    st.markdown("""
<style>

    /* Fix metric label text */
    div[data-testid="stMetricLabel"] > p {
        color: #000 !important;
        font-weight: 600 !important;
    }

    /* Fix metric value text */
    div[data-testid="stMetricValue"] {
        color: #000 !important;
        font-weight: 700 !important;
    }

    /* Fix metric delta text (+0.10%) */
    div[data-testid="stMetricDelta"] {
        color: #000 !important;
        font-weight: 600 !important;
    }

    /* Fix any table or highlighted value (like dataframe cells) */
    .stDataFrame td, .stDataFrame th {
        color: #000 !important;
    }

</style>
""", unsafe_allow_html=True)


    st.markdown("## ⚠ Alerts & Strategy Notifications")
    st.markdown(
        "<div style='opacity:0.8;margin-bottom:10px;'>"
        "Run a forecast and automatically detect high-risk price changes."
        "</div>",
        unsafe_allow_html=True
    )

    # ===============================================================
    # 1) PREPARE DATA
    # ===============================================================
    df = price_df.copy()   # df has columns: date, price

    # ===============================================================
    # 2) LOAD OR TRAIN MODEL
    # ===============================================================
    with st.container():
        st.markdown("### 🧠 Model Status")

        try:
            model = load_model()
            st.success("Loaded existing trained Prophet model.")
        except FileNotFoundError:
            st.warning("No saved model found — training now...")
            with st.spinner("Training Prophet model..."):
                model, info = train_and_tune(df, run_grid=False)
            st.success("New model trained and saved successfully!")

    # ===============================================================
    # 3) GENERATE FORECAST
    # ===============================================================
    with st.container():
        st.markdown("### 🔮 Generating Forecast")
        st.info(f"Creating forecast for next **{CFG.FORECAST_DAYS} days**...")

        try:
            fc = forecast(model, df, periods=CFG.FORECAST_DAYS)
        except Exception as e:
            st.error(f"❌ Forecast failed: {e}")
            return

    # fc ALWAYS contains ['ds', 'yhat', 'yhat_lower', 'yhat_upper']

    # ===============================================================
    # 4) EXTRACT FUTURE FORECAST ONLY
    # ===============================================================
    last_date = df["date"].max()   # <-- correct
    future_only = fc[fc["ds"] > last_date].copy()

    if future_only.empty:
        st.error("No future forecast values were produced.")
        return

    future_only["date"] = future_only["ds"].dt.date
    forecast_table = future_only[["date", "yhat"]].rename(columns={"yhat": "forecast"})

    st.markdown("### 📅 Upcoming Forecast")
    st.dataframe(
        forecast_table.set_index("date"),
        width="stretch",
        height=240
    )

    # ===============================================================
    # 5) ALERT CALCULATION
    # ===============================================================
    current_price = float(df["price"].iloc[-1])   # FIXED
    predicted_price = float(forecast_table["forecast"].iloc[-1])
    pct_change = ((predicted_price - current_price) / current_price) * 100

    st.markdown("### 📊 Alert Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"₹{current_price:,.2f}")
    col2.metric("Predicted Price", f"₹{predicted_price:,.2f}")
    col3.metric("Change (%)", f"{pct_change:+.2f}%")

    st.markdown(
        f"<div style='margin-top:5px;font-size:15px;'>"
        f"Alert threshold: <b>{CFG.EMAIL_THRESHOLD_PCT}%</b>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ===============================================================
    # 6) ALERT BOX (UI)
    # ===============================================================
    st.markdown("---")

    if abs(pct_change) >= CFG.EMAIL_THRESHOLD_PCT:

        # Risk Alert UI Box
        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:10px;
                background-color:#ffe4e4;
                border-left:6px solid #d90429;
                margin-bottom:20px;
            ">
                <b>⚠ HIGH-RISK ALERT</b><br>
                Price expected to change by <b>{pct_change:+.2f}%</b>, 
                exceeding your alert threshold.
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("📧 Send Email Alert"):
            ok, msg = send_email_alert(
                "Product Price Alert",
                current_price,
                predicted_price,
                pct_change
            )
            if ok:
                st.success("Email sent successfully!")
            else:
                st.error(f"Email failed: {msg}")

    else:
        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:10px;
                background-color:#e7ffe7;
                border-left:6px solid #2b9348;
                margin-bottom:20px;
            ">
                ✔ Price change <b>{pct_change:+.2f}%</b> is within safe range.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ===============================================================
    # 7) DOWNLOAD FORECAST
    # ===============================================================
    st.markdown("### ⬇ Download Forecast Data")

    csv = fc.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Full Forecast CSV",
        csv,
        "forecast.csv",
        "text/csv"
    )
