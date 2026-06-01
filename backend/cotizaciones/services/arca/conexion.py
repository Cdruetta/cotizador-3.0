import os
from afip import Afip

def get_afip(config):
    opts = {
        'CUIT': int(config.cuit.replace('-', '')),
        'production': config.ambiente == 'produccion',
        'access_token': os.environ.get('AFIP_ACCESS_TOKEN', ''),
    }
    for campo, clave in [('certificado', 'cert'), ('clave_privada', 'key')]:
        f = getattr(config, campo, None)
        if f and f.path:
            try:
                with open(f.path) as fh:
                    opts[clave] = fh.read()
            except (FileNotFoundError, OSError):
                pass  # archivo no disponible, se omite
    return Afip(opts)

def probar_conexion(config):
    try:
        afip = get_afip(config)
        ultimo = afip.ElectronicBilling.getLastVoucher(config.punto_venta, 11)
        return True, f"Conexión OK. Último comprobante Nº {ultimo}"
    except Exception as e:
        return False, str(e)

def autorizar_factura(config, factura):
    """Envía la factura a AFIP y guarda el CAE."""
    try:
        afip = get_afip(config)
        items = [
            {
                'quantity': float(i.cantidad),
                'description': i.descripcion,
                'net_price': float(i.precio_unit),
                'total_price': float(i.subtotal),
                'iva_id': 3,  # 0% para Monotributo
            }
            for i in factura.items.all()
        ]
        cliente = factura.cliente
        cuit_cliente = getattr(cliente, 'cuit', None)
        if cuit_cliente:
            doc_nro = int(cuit_cliente.replace('-', ''))
        else:
            doc_nro = 0
        data = {
            'CbteTipo': 11,  # Factura C
            'PtoVta': factura.punto_venta,
            'CbteFch': factura.fecha.strftime('%Y%m%d'),
            'Concepto': 1,  # 1=Productos, 2=Servicios, 3=Ambos
            'DocTipo': 80,  # CUIT
            'DocNro': doc_nro,
            'ImpNeto': float(factura.neto),
            'ImpIVA': 0,
            'ImpTotal': float(factura.total),
            'MonId': 'PES',
            'MonCotiz': 1,
        }
        resultado = afip.ElectronicBilling.createNextVoucher(data)
        factura.cae = resultado['CAE']
        factura.cae_vencimiento = resultado['CAEFchVto']
        factura.numero = resultado['voucherNumber']
        factura.estado = 'autorizada'
        factura.save()
        return True, "Factura autorizada correctamente."
    except Exception as e:
        return False, str(e)