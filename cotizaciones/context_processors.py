import json
import urllib.request
from datetime import datetime

def info_extra(request):
    # --- Cotización del dólar ---
    try:
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares", timeout=5) as response:
            data = json.loads(response.read())

        # Buscar oficial, blue y bolsa
        dolar = {
            "oficial": next(item["venta"] for item in data if item["casa"] == "oficial"),
            "blue": next(item["venta"] for item in data if item["casa"] == "blue"),
            "mep": next(item["venta"] for item in data if item["casa"] == "bolsa"),
        }
    except Exception as e:
        print("Error dólar:", e)  # 🔎 para debug
        dolar = {"blue": "N/D", "oficial": "N/D", "mep": "N/D"}

    # --- Clima (Río Cuarto con Open-Meteo) ---
    try:
        with urllib.request.urlopen(
            "https://api.open-meteo.com/v1/forecast?latitude=-33.13&longitude=-64.35&current_weather=true",
            timeout=5
        ) as response:
            clima_data = json.loads(response.read())["current_weather"]

            codigos = {
                0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
                45: "Niebla", 48: "Niebla con escarcha", 51: "Llovizna ligera",
                61: "Lluvia ligera", 71: "Nieve ligera", 80: "Chaparrones",
            }

            clima = {
                "temp": clima_data["temperature"],
                "descripcion": codigos.get(clima_data["weathercode"], "Clima actual")
            }
    except Exception as e:
        print("Error clima:", e)  # 🔎 debug
        clima = {"temp": "N/D", "descripcion": "No disponible"}

    return {"dolar": dolar, "clima": clima}

def global_context(request):
    return {"fecha": datetime.now()}
