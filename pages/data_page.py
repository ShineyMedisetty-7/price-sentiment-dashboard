# ---- pages/data_page.py ----
import streamlit as st
from data.price_loader import load_price
from config import CFG

def render(price_df):
    st.subheader("Raw Data & Exports")
    st.write("Price data (first / last 10 rows)")
    st.dataframe(price_df.head(10).reset_index(drop=True))
    st.download_button("Download price CSV", price_df.to_csv(index=False).encode('utf-8'), "price_export.csv", "text/csv")

    try:
        reviews = load_price(CFG.REVIEW_FILE)
        st.write("Reviews file loaded.")
        st.download_button("Download reviews CSV", reviews.to_csv(index=False).encode('utf-8'), "reviews_export.csv", "text/csv")
    except Exception:
        st.info("No reviews file found or could not load.")
