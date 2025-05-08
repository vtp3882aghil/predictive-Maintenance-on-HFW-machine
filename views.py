from django.shortcuts import render

# Create your views here.
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from django.http import JsonResponse

# ✅ Load and forecast function
def forecast_arima(series, order, steps):
    model = ARIMA(series, order=order)
    model_fit = model.fit()
    return model_fit.forecast(steps=steps)

def run_predictions(request):
    # Load FFT Data
    fft_file = "staticfiles/data/fft_data.csv"
    fft_df = pd.read_csv(fft_file, parse_dates=['time'], index_col='time')
    fft_df = fft_df.tail(14000)

    # Load Temperature Data
    temp_file = "staticfiles/data/motor_temperature.csv"
    temp_df = pd.read_csv(temp_file, parse_dates=['time'], index_col='time')
    temp_df = temp_df.tail(1000)

    # Forecast settings
    forecast_horizon = 14400  # Predict 10 days
    arima_order = (5, 1, 0)  # ARIMA(5,1,0)

    # ✅ Fault Ranges for Vibration
    fault_ranges = {
        (0, 50): "Shaft unbalance, misalignment",
        (50, 250): "Bearing wear, mechanical looseness",
        (250, 1000): "Gear faults, resonance, electrical issues",
        (1000, 1600): "High-frequency bearing defects, structural resonance"
    }

    # ✅ Temperature Ranges
    temp_ranges = {
        (30, 50): "Idle/No Load",
        (50, 80): "Normal Load",
        (80, 110): "Heavy Load",
        (110, 150): "Overloaded",
        (150, 180): "Critical/Overheating (Risk of Failure)"
    }

    # ✅ Predictions Storage
    predictions = {"vibration": {}, "temperature": {}}

    # ✅ Vibration Prediction
    for motor in ['f1', 'f2', 'f3']:
        forecast_values = forecast_arima(fft_df[motor], arima_order, forecast_horizon)
        future_timestamps = pd.date_range(fft_df.index[-1], periods=forecast_horizon, freq='min')

        # Detect fault condition
        fault_detected = None
        for i, freq in enumerate(forecast_values):
            for (low, high), fault_type in fault_ranges.items():
                if low <= freq < high:
                    fault_detected = {"fault": fault_type, "time": future_timestamps[i].strftime('%Y-%m-%d %H:%M')}
                    break
            if fault_detected:
                break

        predictions["vibration"][motor] = fault_detected if fault_detected else "No major fault detected"

    # ✅ Temperature Prediction
    for motor in ['t1', 't2', 't3']:
        forecast_values = forecast_arima(temp_df[motor], arima_order, forecast_horizon)
        future_timestamps = pd.date_range(temp_df.index[-1], periods=forecast_horizon, freq='min')

        # Detect temperature condition
        temp_condition = None
        for i, temp in enumerate(forecast_values):
            for (low, high), condition in temp_ranges.items():
                if low <= temp < high:
                    temp_condition = {"condition": condition, "time": "in 10 days range "}
                    break
            if temp_condition:
                break

        predictions["temperature"][motor] = temp_condition if temp_condition else "No overheating detected"

    return JsonResponse(predictions)
