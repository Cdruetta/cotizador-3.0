import json
import urllib.request
from datetime import datetime

def info_extra(request):
    # --- Cotización del dólar ---
    try:
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares/oficial", timeout=5) as response:
            oficial = json.loads(response.read())
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares/blue", timeout=5) as response:
            blue = json.loads(response.read())
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares/bolsa", timeout=5) as response:
            bolsa = json.loads(response.read())    

        dolar = {
            "blue": blue["venta"],
            "oficial": oficial["venta"],
            "mep": bolsa["venta"] 
}
    except Exception:
        dolar = {"blue": "N/D", "oficial": "N/D", "mep": "N/D"}

    # --- Clima (ejemplo: Río Cuarto con Open-Meteo) ---
    try:
        with urllib.request.urlopen(
            "https://api.open-meteo.com/v1/forecast?latitude=-33.13&longitude=-64.35&current_weather=true",
            timeout=5
        ) as response:
            clima_data = json.loads(response.read())["current_weather"]

            # Traducir weathercode a descripción
            codigos = {
                0: "Despejado",
                1: "Mayormente despejado",
                2: "Parcialmente nublado",
                3: "Nublado",
                45: "Niebla",
                48: "Niebla con escarcha",
                51: "Llovizna ligera",
                61: "Lluvia ligera",
                71: "Nieve ligera",
                80: "Chaparrones",
            }

            clima = {
                "temp": clima_data["temperature"],
                "descripcion": codigos.get(clima_data["weathercode"], "Clima actual")
            }
    except Exception:
        clima = {"temp": "N/D", "descripcion": "No disponible"}

    return {
        "dolar": dolar,
        "clima": clima
    }

def global_context(request):
    return {
        "fecha": datetime.now()
    }
