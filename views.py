from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings
from django.http import JsonResponse

def get_fft_data(request):
    """Reads FFT data from CSV and returns JSON response for live updates."""
    try:
        csv_path = os.path.join(settings.STATIC_ROOT, "data", "fft_data.csv")

        if not os.path.exists(csv_path):
            return JsonResponse({"error": "CSV file not found!"}, status=500)

        df = pd.read_csv(csv_path)

        if df.empty:
            return JsonResponse({"error": "CSV file is empty!"}, status=500)

        df = df.tail(60)  # Keep only the latest 60 records

        data = {
            "timestamps": df["time"].astype(str).tolist(),
            "f1": df["f1"].tolist(),
            "f2": df["f2"].tolist(),
            "f3": df["f3"].tolist(),
        }
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def live_plot(request):
    """Renders the live plot page."""
    return render(request, 'machine/plot.html')


def machine_view(req):
    return render(req,'machine/machine_view.html')


def get_temperature_data(request):
    """Reads Temperature data from CSV and returns JSON response for live updates."""
    try:
        csv_path = os.path.join(settings.STATIC_ROOT, "data", "motor_temperature.csv")

        if not os.path.exists(csv_path):
            return JsonResponse({"error": "CSV file not found!"}, status=500)

        df = pd.read_csv(csv_path)

        if df.empty:
            return JsonResponse({"error": "CSV file is empty!"}, status=500)

        df = df.tail(60)  # Keep only the latest 60 records

        data = {
            "timestamps": df["time"].astype(str).tolist(),
            "t1": df["t1"].tolist(),
            "t2": df["t2"].tolist(),
            "t3": df["t3"].tolist(),
        }
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

