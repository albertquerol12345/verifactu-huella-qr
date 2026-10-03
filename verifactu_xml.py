"""XML de los registros VERI*FACTU (RegistroAlta y RegistroAnulacion) dentro de RegFactuSistemaFacturacion,
con la huella encadenada calculada por verifactu_huella.py y validado contra los esquemas XSD de la AEAT (carpeta xsd/).

Cubre el caso común: factura completa (F1) o simplificada (F2) con IVA en régimen general (clave 01, operación S1)
y uno o varios tipos. Para rectificativas, operaciones exentas, recargo de equivalencia o terceros, amplía `detalle`.
No firma ni envía: el envío al servicio web de la AEAT necesita un certificado electrónico (ver README).
Licencia MIT. Requiere lxml solo para validar (pip install lxml).
"""
from xml.sax.saxutils import escape
from verifactu_huella import huella_alta, huella_anulacion

SF = "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd"
SFLR = "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroLR.xsd"


def _e(tag, valor):
    return f"<sf:{tag}>{escape(str(valor).strip())}</sf:{tag}>"


def _sistema(s):
    """s: dict con NombreRazon, NIF, NombreSistemaInformatico, IdSistemaInformatico, Version, NumeroInstalacion,
    TipoUsoPosibleSoloVerifactu, TipoUsoPosibleMultiOT, IndicadorMultiplesOT (S/N)."""
    orden = ["NombreRazon", "NIF", "NombreSistemaInformatico", "IdSistemaInformatico", "Version", "NumeroInstalacion",
             "TipoUsoPosibleSoloVerifactu", "TipoUsoPosibleMultiOT", "IndicadorMultiplesOT"]
    return "<sf:SistemaInformatico>" + "".join(_e(k, s[k]) for k in orden) + "</sf:SistemaInformatico>"


def _encadenamiento(anterior):
    """anterior: None si es el primer registro del sistema; si no, dict con IDEmisorFactura, NumSerieFactura,
    FechaExpedicionFactura y Huella del registro anterior."""
    if not anterior:
        return "<sf:Encadenamiento><sf:PrimerRegistro>S</sf:PrimerRegistro></sf:Encadenamiento>"
    return ("<sf:Encadenamiento><sf:RegistroAnterior>" + "".join(_e(k, anterior[k]) for k in
            ["IDEmisorFactura", "NumSerieFactura", "FechaExpedicionFactura", "Huella"]) + "</sf:RegistroAnterior></sf:Encadenamiento>")


def registro_alta(nif_emisor, nombre_emisor, num_serie, fecha_expedicion, descripcion, lineas_iva, sistema,
                  fecha_hora_huso, anterior=None, tipo_factura="F1", destinatario=None):
    """lineas_iva: lista de (tipo_impositivo, base, cuota) como cadenas con punto decimal, p. ej. [("21.00", "100.00", "21.00")].
    destinatario: (nombre, nif) obligatorio en F1. Devuelve (xml_del_registro, huella)."""
    cuota = f"{sum(float(c) for _, _, c in lineas_iva):.2f}"
    total = f"{sum(float(b) + float(c) for _, b, c in lineas_iva):.2f}"
    huella = huella_alta(IDEmisorFactura=nif_emisor, NumSerieFactura=num_serie, FechaExpedicionFactura=fecha_expedicion,
                         TipoFactura=tipo_factura, CuotaTotal=cuota, ImporteTotal=total,
                         Huella=(anterior or {}).get("Huella", ""), FechaHoraHusoGenRegistro=fecha_hora_huso)
    dest = ""
    if destinatario:
        dest = ("<sf:Destinatarios><sf:IDDestinatario>" + _e("NombreRazon", destinatario[0]) + _e("NIF", destinatario[1])
                + "</sf:IDDestinatario></sf:Destinatarios>")
    desglose = "".join(
        "<sf:DetalleDesglose>" + _e("Impuesto", "01") + _e("ClaveRegimen", "01") + _e("CalificacionOperacion", "S1")
        + _e("TipoImpositivo", t) + _e("BaseImponibleOimporteNoSujeto", b) + _e("CuotaRepercutida", c) + "</sf:DetalleDesglose>"
        for t, b, c in lineas_iva)
    xml = ("<sf:RegistroAlta>" + _e("IDVersion", "1.0")
           + "<sf:IDFactura>" + _e("IDEmisorFactura", nif_emisor) + _e("NumSerieFactura", num_serie)
           + _e("FechaExpedicionFactura", fecha_expedicion) + "</sf:IDFactura>"
           + _e("NombreRazonEmisor", nombre_emisor) + _e("TipoFactura", tipo_factura) + _e("DescripcionOperacion", descripcion)
           + dest + "<sf:Desglose>" + desglose + "</sf:Desglose>" + _e("CuotaTotal", cuota) + _e("ImporteTotal", total)
           + _encadenamiento(anterior) + _sistema(sistema) + _e("FechaHoraHusoGenRegistro", fecha_hora_huso)
           + _e("TipoHuella", "01") + _e("Huella", huella) + "</sf:RegistroAlta>")
    return xml, huella


def registro_anulacion(nif_emisor, num_serie, fecha_expedicion, sistema, fecha_hora_huso, anterior):
    """Anula una factura ya registrada. anterior: registro inmediatamente anterior de la cadena. Devuelve (xml, huella)."""
    huella = huella_anulacion(IDEmisorFacturaAnulada=nif_emisor, NumSerieFacturaAnulada=num_serie,
                              FechaExpedicionFacturaAnulada=fecha_expedicion, Huella=anterior["Huella"],
                              FechaHoraHusoGenRegistro=fecha_hora_huso)
    xml = ("<sf:RegistroAnulacion>" + _e("IDVersion", "1.0")
           + "<sf:IDFactura>" + _e("IDEmisorFacturaAnulada", nif_emisor) + _e("NumSerieFacturaAnulada", num_serie)
           + _e("FechaExpedicionFacturaAnulada", fecha_expedicion) + "</sf:IDFactura>"
           + _encadenamiento(anterior) + _sistema(sistema) + _e("FechaHoraHusoGenRegistro", fecha_hora_huso)
           + _e("TipoHuella", "01") + _e("Huella", huella) + "</sf:RegistroAnulacion>")
    return xml, huella


def documento(nif_obligado, nombre_obligado, registros_xml):
    """RegFactuSistemaFacturacion con la cabecera y hasta 1.000 registros (cuerpo del mensaje SOAP)."""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<sfLR:RegFactuSistemaFacturacion xmlns:sfLR="{SFLR}" xmlns:sf="{SF}">'
            "<sfLR:Cabecera><sf:ObligadoEmision>" + _e("NombreRazon", nombre_obligado) + _e("NIF", nif_obligado)
            + "</sf:ObligadoEmision></sfLR:Cabecera>"
            + "".join(f"<sfLR:RegistroFactura>{r}</sfLR:RegistroFactura>" for r in registros_xml)
            + "</sfLR:RegFactuSistemaFacturacion>")


def validar(xml_texto, carpeta_xsd="xsd"):
    """Valida contra SuministroLR.xsd. Devuelve lista de errores (vacía si es válido)."""
    from pathlib import Path
    from lxml import etree
    base = Path(__file__).parent / carpeta_xsd
    esquema = etree.XMLSchema(etree.parse(str(base / "SuministroLR.xsd")))
    doc = etree.fromstring(xml_texto.encode("utf-8"))
    return [] if esquema.validate(doc) else [str(e) for e in esquema.error_log]
