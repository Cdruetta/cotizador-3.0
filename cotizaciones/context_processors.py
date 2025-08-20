import requests

def info_extra(request):
    # --- Cotización del dólar ---
    try:
        r = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=5)
        data = r.json()
        dolar = {
            "blue": data["blue"]["value_sell"],
            "oficial": data["oficial"]["value_sell"]
        }
    except Exception:
        dolar = {"blue": "N/D", "oficial": "N/D"}

    # --- Clima (ejemplo: Río Cuarto) ---
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=-33.13&longitude=-64.35&current_weather=true",
            timeout=5
        )
        clima_data = r.json()["current_weather"]
        clima = {
            "temp": clima_data["temperature"],
            "descripcion": "Clima actual",
        }
    except Exception:
        clima = {"temp": "N/D", "descripcion": "No disponible"}

    return {
        "dolar": dolar,
        "clima": clima
    }
