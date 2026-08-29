# ---- data/review_loader.py ----
import pandas as pd
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data(ttl=3600)
def load_reviews(file):
    df = pd.read_csv(file)
    return df

def combine_text_columns(df):
    dfc = df = df.copy()
    # prefer common names
    text_cols = [c for c in dfc.columns if c.lower() in ('title','review','comments','text','content','body')]
    if not text_cols:
        text_cols = [c for c in dfc.columns if dfc[c].dtype == object][:1]
    if text_cols:
        dfc['full_review'] = dfc[text_cols].astype(str).agg(' '.join, axis=1)
    else:
        dfc['full_review'] = dfc.astype(str).agg(' '.join, axis=1)
    dfc['full_review'] = dfc['full_review'].str.strip()
    dfc = dfc[dfc['full_review'].str.len() > 0].reset_index(drop=True)
    return dfc

def extract_topics(texts, top_n=20):
    combined = ' '.join(texts.astype(str).tolist()).lower()
    combined = re.sub(r'[^a-z0-9\s]', ' ', combined)
    words = combined.split()
    stop = set([
        'the','this','that','for','with','have','from','your','you','are','was',
        'were','but','and','not','what','has','had','its','will','can','also',
        'one','get','gets','using','hp','victus','laptop'
    ])
    filtered = [w for w in words if w not in stop and len(w) > 3]
    freq = Counter(filtered)
    return freq.most_common(top_n)

def generate_wordcloud(texts):
    if len(texts) == 0:
        return None
    wc = WordCloud(width=800, height=400, background_color='white').generate(' '.join(texts))
    return wc

def plot_wordcloud(wc):
    if wc is None:
        return None
    plt.figure(figsize=(10,4))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    return plt
