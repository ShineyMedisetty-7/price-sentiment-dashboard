# ---- app.py ----
import streamlit as st
from config import CFG
from styles import inject_css
from data.price_loader import load_price, compute_kpis
from pages import overview_page, forecast_page, sentiment_page, data_page, alerts_page
import pandas as pd

# ---------------------------------------------------------
# IMPORTANT: Page config MUST be called before anything else
# ---------------------------------------------------------
st.set_page_config(
    page_title="Price & Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Inject custom CSS AFTER page_config
    inject_css()

    # Sidebar Navigation
    with st.sidebar:
        st.title("📊 Dashboard")
        page = st.radio(
            "Go to",
            ["Overview", "Forecast", "Sentiment", "Data", "Alerts & Export"],
            index=0
        )

        st.divider()
        st.markdown("**Files**")
        st.markdown(f"- Price file: `{CFG.PRICE_FILE}`")
        st.markdown(f"- Reviews file: `{CFG.REVIEW_FILE}`")

        st.divider()
        st.markdown("**Email alerts**")
        st.markdown(
            "Set env vars: ALERT_EMAIL_FROM, ALERT_EMAIL_PASSWORD, ALERT_EMAIL_TO, ALERT_EMAIL_THRESHOLD_PCT"
        )

    # Load Price Data
    try:
        price_df = load_price(CFG.PRICE_FILE)
    except Exception as e:
        st.error(f"Could not load price data: {e}")
        st.stop()

    kpis = compute_kpis(price_df)

    # Header
    st.markdown(
        "<div class='header'>"
        "<h1 style='margin:0'>✨ Price & Sentiment Dashboard</h1>"
        "<div style='opacity:0.9;margin-top:6px'>Prophet Forecast · Transformers Sentiment · Email Alerts</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Page Routing
    if page == "Overview":
        overview_page.render(price_df, kpis)
    elif page == "Forecast":
        forecast_page.render(price_df)
    elif page == "Sentiment":
        sentiment_page.render()
    elif page == "Data":
        data_page.render(price_df)
    elif page == "Alerts & Export":
        alerts_page.render(price_df)


if __name__ == "__main__":
    main()
