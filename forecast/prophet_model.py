import pandas as pd
from prophet import Prophet

def train_prophet_model(df):

    dfp = df.rename(columns={'date':'ds','price':'y'}).copy()
    dfp['ds'] = pd.to_datetime(dfp['ds'])

    # Feature engineering (already calculated in df)
    regressors = ['competitor_price', 'discount', 'sentiment', 'MA7', 'MA30']

    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.7,
        seasonality_mode='multiplicative',
        interval_width=0.95
    )

    for col in regressors:
        if col in dfp.columns:
            m.add_regressor(col)

    m.fit(dfp)
    return m
