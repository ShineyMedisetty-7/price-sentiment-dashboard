# forecast/prophet_model_improved.py

import pandas as pd
import pickle
import math
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from sklearn.metrics import mean_squared_error
from pathlib import Path

# Base engineered regressors
REGRESSORS_BASE = ['MA7', 'MA30', 'lag1', 'lag7', 'pct_change', 'volatility_7']

# Optional external regressors (if CSV provides)
EXTERNAL_REGRESSORS = ['competitor_price', 'discount', 'sentiment_score']

# Model save path
MODEL_PATH = Path(__file__).resolve().parent / "prophet_best_model.pkl"


# -------------------------------------------------------------
# PREPARE DATAFRAME
# -------------------------------------------------------------
def prepare_df(path_or_df):
    """
    Accept a CSV path or DataFrame with columns ['date', 'price'].
    Returns a cleaned, daily-resampled df with engineered features.
    Keeps optional external regressors if present.
    """
    # Load input
    if isinstance(path_or_df, (str, Path)):
        df = pd.read_csv(path_or_df)
    else:
        df = path_or_df.copy()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    if 'date' not in df.columns or 'price' not in df.columns:
        raise ValueError("CSV must contain 'date' and 'price' columns.")

    # Keep known columns and any external regs
    cols_keep = ['date', 'price'] + [c for c in EXTERNAL_REGRESSORS if c in df.columns]
    df = df[cols_keep].rename(columns={'date': 'ds', 'price': 'y'})

    # Convert and clean date
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce').dt.normalize()
    df = df.dropna(subset=['ds', 'y']).sort_values('ds')

    # Daily resampling to ensure Prophet consistency
    df = df.set_index('ds').resample('D').last().interpolate().ffill().bfill().reset_index()

    # -------------------------------------------------------------
    # Feature Engineering (NaN-proof)
    # -------------------------------------------------------------

    # Moving averages
    df['MA7'] = df['y'].rolling(7, min_periods=1).mean()
    df['MA30'] = df['y'].rolling(30, min_periods=1).mean()

    # Safe lag features
    df['lag1'] = df['y'].shift(1)
    df['lag7'] = df['y'].shift(7)

    # Fill NaN lags with current values (best fallback for Prophet)
    df['lag1'] = df['lag1'].fillna(df['y'])
    df['lag7'] = df['lag7'].fillna(df['y'])

    # Price % change (no NaN)
    df['pct_change'] = df['y'].pct_change().fillna(0)

    # 7-day volatility (std)
    df['volatility_7'] = df['y'].rolling(7, min_periods=1).std().fillna(0)

    # Final cleanup — ensure NO NaN anywhere
    df = df.ffill().bfill()

    return df


# -------------------------------------------------------------
# TRAIN + (OPTIONAL) GRID TUNE
# -------------------------------------------------------------
def train_and_tune(df, run_grid=True):
    """
    Train Prophet model using engineered regressors.
    If run_grid=True, performs fast grid search.
    Returns (trained_model, metrics_dict).
    """
    dfp = prepare_df(df)

    # Baseline model for comparison
    baseline = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        interval_width=0.95
    )
    baseline.fit(dfp[['ds', 'y']])

    fut_base = baseline.make_future_dataframe(periods=90, freq='D')
    pred_base = baseline.predict(fut_base)

    merged_base = pd.merge(
        pred_base[['ds', 'yhat']],
        dfp[['ds', 'y']],
        on='ds',
        how='inner'
    )

    eval_base = merged_base[merged_base['ds'] >= (dfp['ds'].max() - pd.Timedelta(days=89))]
    rmse_baseline = math.sqrt(mean_squared_error(eval_base['y'], eval_base['yhat']))

    # Candidate regressors
    regressors = REGRESSORS_BASE + [c for c in EXTERNAL_REGRESSORS if c in dfp.columns]

    # Default params found during tuning experiments
    default_params = {'cps': 0.05, 'seasonality_mode': 'additive', 'sps': 1.0}

    # -------------------------------------------------------------
    # FAST TRAIN (no grid search)
    # -------------------------------------------------------------
    if not run_grid:
        m = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=default_params['cps'],
            seasonality_mode=default_params['seasonality_mode'],
            seasonality_prior_scale=default_params['sps'],
            interval_width=0.95
        )

        for r in regressors:
            m.add_regressor(r)

        m.fit(dfp[['ds', 'y'] + regressors])
        save_model(m)

        return m, {
            'rmse_baseline_last90': rmse_baseline,
            'best_params': default_params,
            'rmse_cv_best': None
        }

    # -------------------------------------------------------------
    # GRID SEARCH (fast tuning)
    # -------------------------------------------------------------
    param_grid = [
        {'cps': 0.05, 'seasonality_mode': 'additive', 'sps': 1.0},
        {'cps': 0.5,  'seasonality_mode': 'additive', 'sps': 10.0},
        {'cps': 1.0,  'seasonality_mode': 'additive', 'sps': 10.0},
    ]

    best = {'rmse': float('inf'), 'params': None, 'model': None}
    summary = []

    for params in param_grid:
        m = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=params['cps'],
            seasonality_mode=params['seasonality_mode'],
            seasonality_prior_scale=params['sps'],
            interval_width=0.95
        )

        for r in regressors:
            m.add_regressor(r)

        m.fit(dfp[['ds', 'y'] + regressors])

        # Try cross-validation
        try:
            initial_days = max(int(len(dfp) * 0.6), 365)
            df_cv = cross_validation(
                m,
                initial=f"{initial_days} days",
                period="30 days",
                horizon="30 days",
                parallel="processes"
            )
            perf = performance_metrics(df_cv)
            rmse = float(perf['rmse'].iloc[-1])
        except Exception:
            # Fallback to simple RMSE
            fut = m.make_future_dataframe(periods=0)
            pred = m.predict(fut)
            merged = pd.merge(pred[['ds', 'yhat']], dfp[['ds', 'y']], on='ds')
            rmse = math.sqrt(mean_squared_error(merged['y'], merged['yhat']))

        summary.append({'params': params, 'rmse': rmse})

        if rmse < best['rmse']:
            best = {'rmse': rmse, 'params': params, 'model': m}

    save_model(best['model'])

    return best['model'], {
        'rmse_baseline_last90': rmse_baseline,
        'best_params': best['params'],
        'rmse_cv_best': best['rmse'],
        'grid_summary': summary
    }


# -------------------------------------------------------------
# FORECAST
# -------------------------------------------------------------
def forecast(model, df, periods=90, future_regressors=None):
    """
    Generate Prophet forecast with future regressors.
    If user does not provide future values, last known values are repeated.
    Returns forecast dataframe with ds, yhat, yhat_lower, yhat_upper.
    """
    dfp = prepare_df(df)
    regressors = REGRESSORS_BASE + [c for c in EXTERNAL_REGRESSORS if c in dfp.columns]

    future = model.make_future_dataframe(periods=periods, freq='D')
    last = dfp.iloc[-1]

    # default: copy last known regressor values
    for r in regressors:
        future[r] = last[r]

    # If user supplied future_regressors, fill only the future portion
    if future_regressors:
        for r, vals in future_regressors.items():
            if r not in regressors:
                continue
            # accept scalar
            if not hasattr(vals, '__len__') or isinstance(vals, str):
                vals = [vals] * periods
            vals = list(vals)
            if len(vals) != periods:
                raise ValueError(f"future_regressors[{r}] length must equal periods ({periods})")
            # assign to the last `periods` rows of future
            future.loc[future.index[-periods:], r] = vals

    fc = model.predict(future)

    # ensure columns and reset index (robustness)
    fc = fc.reset_index(drop=True)
    required = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    missing = [c for c in required if c not in fc.columns]
    if missing:
        raise ValueError(f"Forecast output missing columns: {missing}")

    return fc[required]


# -------------------------------------------------------------
# SAVE / LOAD MODEL
# -------------------------------------------------------------
def save_model(m):
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(m, f)


def load_model():
    if MODEL_PATH.exists():
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    raise FileNotFoundError("Saved model not found. Train first using train_and_tune().")


# -------------------------------------------------------------
# OPTIONAL CLI USAGE
# -------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--periods", type=int, default=90)
    p.add_argument("--tune", action="store_true")
    args = p.parse_args()

    model, info = train_and_tune(args.csv, run_grid=args.tune)
    print("Training completed. Info:", info)

    fc = forecast(model, args.csv, periods=args.periods)
    fc.to_csv("improved_forecast_tail.csv", index=False)

    print("Saved improved_forecast_tail.csv")
