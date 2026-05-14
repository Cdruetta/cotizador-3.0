from datetime import datetime


def info_extra(request):
    """Evitar que cada request haga llamados externos lentos.

    Si necesitas dolar/clima, conviene cachearlos o moverlos a un endpoint JS.
    Por ahora devolvemos N/D para que el navbar/topbar no frene la app.
    """
    return {
        "dolar": {"blue": "N/D", "oficial": "N/D", "bolsa": "N/D"},
        "clima": {"temp": "N/D", "descripcion": "No disponible"},
    }


def global_context(request):
    return {"fecha": datetime.now()}



