import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from flask import jsonify
from flask import render_template

app = Flask(__name__)

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 7)  # FUTURE_DAYS=7

    def forward(self, x):
        _, (hn, _) = self.lstm(x)
        return self.fc(hn[-1])

# ========== Load model, scalers, encoder ==========
model = LSTMModel(input_size=10)  # 10 features in train script
model.load_state_dict(torch.load("model/lstm_model.h", map_location='cpu'))
model.eval()

scaler_x = joblib.load("model/scaler_x.pkl")
scaler_y = joblib.load("model/scaler_y.pkl")
city_encoder = joblib.load("model/city_encoder.pkl")

# ========== Load full dataset ==========
df = pd.read_csv("data/aqi_data_for_db.csv")
df['last_updated_day'] = pd.to_datetime(df['last_updated_day'])
df['dayofyear'] = df['last_updated_day'].dt.dayofyear
df['month'] = df['last_updated_day'].dt.month
df.sort_values(by=['city', 'last_updated_day'], inplace=True)

statemap = {
    "Delhi": 1,
    "Kolkata": 2,
    "Bangalore": 0,
    # add other cities as needed
}
def format_predictions_with_dates(predicted_aqi, last_date_str):
    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
    formatted = []
    for i, aqi in enumerate(predicted_aqi, 1):
        date = last_date + timedelta(days=i)
        formatted.append({
            'date': date.strftime('%Y-%m-%d'),
            'predicted_aqi': round(aqi)
        })
    return formatted

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    city = data.get('city')
    date_str = data.get('date')  # format: 'YYYY-MM-DD'
    date = pd.to_datetime(date_str)

    if city not in statemap:
        return jsonify({"error": "Unknown city"}), 400
    city_encoded = statemap[city]
    df['city_encoded'] = df['city'].map(statemap)

    # Filter data for this city before the input date
    city_df = df[df['city_encoded'] == city_encoded]
    past_days_df = city_df[city_df['last_updated_day'] <= date].tail(30)

    if past_days_df.shape[0] < 30:
        print(f"Insufficient data: found only {past_days_df.shape[0]} rows")
        return jsonify({"status": 200, "predicted_aqi_next_7_days": None, "msg": "insufficient data"})

    if len(past_days_df) < 30:
        return jsonify({"status": 400, "predicted_aqi_next_7_days": None, "error": "Not enough past data"})

    # Prepare features
    feature_cols = ['PM10', 'PM2', 'NO2', 'NH3', 'SO2', 'CO', 'OZONE', 'city_encoded', 'dayofyear', 'month']
    past_features = past_days_df[feature_cols]

    # Scale
    past_scaled = scaler_x.transform(past_features)

    # Model expects batch dimension
    input_tensor = torch.tensor(past_scaled, dtype=torch.float32).unsqueeze(0)

    # Predict
    with torch.no_grad():
        pred_scaled = model(input_tensor).numpy()

    # Inverse scale predictions
    pred_aqi = scaler_y.inverse_transform(pred_scaled).flatten().tolist()

    last_date_str = date_str  # replace with your actual last date
    
    formatted_result = format_predictions_with_dates(pred_aqi, last_date_str)
    
    return jsonify({"status": 200, "predicted_aqi_next_7_days": formatted_result, "msg": "success"})


if __name__ == '__main__':
    app.run(debug=True,port=5005)
