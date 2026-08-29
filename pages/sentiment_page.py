# ---- pages/sentiment_page.py ----
import streamlit as st
import pandas as pd
import plotly.express as px
from data.review_loader import load_reviews, combine_text_columns, extract_topics, generate_wordcloud, plot_wordcloud
from sentiment.sentiment_model import load_sentiment_pipeline, normalize_label
from config import CFG
import matplotlib.pyplot as plt

def render():
    st.markdown("""
<style>

 /* 🔥 Fix TABLE TEXT for 'Key Topics' table in dark mode */
[data-testid="stTable"] td, 
[data-testid="stTable"] th {
    color: #000 !important;
    font-weight: 600 !important;
}

/* For st.table inside columns */
.stTable table td, 
.stTable table th {
    color: #000 !important;
}

/* Optional: Light background for contrast */
.stTable {
    background-color: #f8f8f8 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #000 !important;
}

/* Fix selectbox labels */
div[data-baseweb="select"] label,
div[data-baseweb="input"] label,
label[data-testid="stWidgetLabel"] {
    color: #000 !important;
    font-weight: 600 !important;
}

/* Fix text inside selectbox dropdown */
div[data-baseweb="select"] * {
    color: #000 !important;
}

/* Fix number input label */
div[data-baseweb="input"] * {
    color: #000 !important;
}

/* Fix table text (already working, but enforce it) */
[data-testid="stDataFrame"] td, 
[data-testid="stDataFrame"] th {
    color: #000 !important;
}


</style>
""", unsafe_allow_html=True)

    st.subheader("Sentiment Analysis — Reviews")

    try:
        reviews = load_reviews(CFG.REVIEW_FILE)
    except Exception as e:
        st.error(f"Could not load reviews file: {e}")
        return

    st.markdown("### Sample of raw reviews")
    st.dataframe(reviews.head(10))

    with st.spinner("Loading sentiment model... (this may take a while on first run)"):
        try:
            pipe = load_sentiment_pipeline(CFG.SENTIMENT_MODEL)
        except Exception as e:
            st.error(f"Could not load sentiment model: {e}")
            return

    with st.spinner("Preparing reviews..."):
        dfc = combine_text_columns(reviews)

    if dfc.empty:
        st.info("No textual reviews found.")
        return

    texts = dfc['full_review'].tolist()
    results = []
    for i in range(0, len(texts), CFG.SENTIMENT_BATCH):
        batch = texts[i:i+CFG.SENTIMENT_BATCH]
        r = pipe(batch)
        results.extend(r)

    labels = [normalize_label(r['label']) for r in results]
    scores = [r.get('score', 0.0) for r in results]
    dfc['sentiment'] = labels
    dfc['sentiment_score'] = scores
    dfc['len'] = dfc['full_review'].str.len()
    dfc['words'] = dfc['full_review'].str.split().str.len()

    counts = dfc['sentiment'].value_counts().reindex(['positive','neutral','negative']).fillna(0).astype(int)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Sentiment distribution")
        fig = px.pie(values=counts.values, names=counts.index, color=counts.index,
                     color_discrete_map={'positive':CFG.COLORS['success'],'neutral':'#9CA3AF','negative':CFG.COLORS['danger']})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Key topics")
        topics = extract_topics(dfc['full_review'], top_n=12)
        if topics:
            top_df = pd.DataFrame(topics, columns=['topic','freq'])
            st.table(top_df.head(10))

    st.subheader("Wordcloud (all reviews)")
    wc = generate_wordcloud(dfc['full_review'])
    if wc is not None:
        plt_obj = plot_wordcloud(wc)
        if plt_obj:
            st.pyplot(plt_obj)

    st.subheader("Browse reviews by sentiment")
    choice = st.selectbox("Choose sentiment", options=['all','positive','neutral','negative'])
    if choice == 'all':
        df_view = dfc
    else:
        df_view = dfc[dfc['sentiment'] == choice]

    per_page = st.selectbox("Rows per page", [5,10,20,50], index=1)
    total = len(df_view)
    pages = max(1, (total + per_page - 1)//per_page)
    page_num = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)
    start = (page_num-1)*per_page
    end = start + per_page
    st.write(f"Showing {start+1} — {min(end,total)} of {total}")
    show_df = df_view[['full_review','sentiment','sentiment_score']].iloc[start:end].reset_index(drop=True)
    st.dataframe(show_df.rename(columns={'full_review':'review'}))

    csv = dfc.to_csv(index=False).encode('utf-8')
    st.download_button("Download analyzed reviews CSV", csv, "analyzed_reviews.csv", "text/csv")
