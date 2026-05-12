from afip import Afip

def get_afip(config):
    return Afip({
        'CUIT': int(config.cuit.replace('-', '')),
        'cert': config.certificado.path,
        'key': config.clave_privada.path,
        'production': config.ambiente == 'produccion',
    })

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
        data = {
            'CbteDesde': None,  # afip-py lo resuelve solo
            'CbteHasta': None,
            'CbteFch': factura.fecha.strftime('%Y%m%d'),
            'ImpTotal': float(factura.total),
            'ImpNeto': float(factura.neto),
            'ImpIVA': 0,
            'MonId': 'PES',
            'MonCotiz': 1,
        }
        resultado = afip.ElectronicBilling.createVoucher(data)
        factura.cae = resultado['CAE']
        factura.cae_vencimiento = resultado['CAEFchVto']
        factura.numero = resultado['CbteDesde']
        factura.estado = 'autorizada'
        factura.save()
        return True, "Factura autorizada correctamente."
    except Exception as e:
        return False, str(e)