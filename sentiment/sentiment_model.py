# ---- sentiment/sentiment_model.py ----
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from config import CFG

@st.cache_resource
def load_sentiment_pipeline(model_name: str = CFG.SENTIMENT_MODEL):
    """
    Loads and returns a Transformers sentiment-analysis pipeline.
    Caches the pipeline as a Streamlit resource.
    """
    device = 0 if torch.cuda.is_available() else -1
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=device, truncation=True, max_length=128)
    return pipe

def normalize_label(label: str):
    lab = label.lower()
    if 'neg' in lab:
        return 'negative'
    if 'neu' in lab:
        return 'neutral'
    if 'pos' in lab:
        return 'positive'
    return lab
