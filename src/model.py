import os
import joblib
from prophet import Prophet

MODEL_PATH = "models/crime_forecast.pkl"

def train_model(daily_counts, date_col="ds", target_col="y", save_path=MODEL_PATH):
    """Train Prophet model dynamically"""
    # Prepare dataset
    df = daily_counts.rename(columns={date_col: "ds", target_col: "y"})
    df = df[["ds", "y"]]

    # Train model
    model = Prophet()
    model.fit(df)

    # Save model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)

    return model

def load_model(save_path=MODEL_PATH):
    """Load trained model"""
    if os.path.exists(save_path):
        return joblib.load(save_path)
    return None

def forecast_future(model, periods=30):
    """Forecast future crimes"""
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast
