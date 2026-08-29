# ---- config.py ----
import os

class CFG:
    # Files
    PRICE_FILE = "HP_Victus.csv"          
    REVIEW_FILE = "hp_laptop_reviews (1).csv"  

    # Forecasting
    FORECAST_DAYS = 7
    KPIS_WINDOW = 7

    # Sentiment
    SENTIMENT_MODEL = "finiteautomata/bertweet-base-sentiment-analysis"
    SENTIMENT_BATCH = 32

    # Email
    EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "")
    EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD", "")
    EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
    EMAIL_THRESHOLD_PCT = float(os.getenv("ALERT_EMAIL_THRESHOLD_PCT", "0.05"))

    # UI Colors
    COLORS = {
        "primary": "#5b21b6",
        "accent": "#7c3aed",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "muted": "#6b7280",
        "bg": "#f8fafc"
    }
