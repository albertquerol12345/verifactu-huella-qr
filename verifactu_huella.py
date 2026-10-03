"""Huella (hash) SHA-256 de los registros VERI*FACTU y URL del QR tributario, según la AEAT.

- Huella: «Detalle de las especificaciones técnicas para generación de la huella o hash de los
  registros de facturación», v0.1.2 (27-08-2024). Cadena «campo=valor&...» en el orden fijado,
  valores sin espacios al inicio y al final, campo vacío = «campo=», UTF-8, SHA-256, hex en mayúsculas.
- QR: «Detalle de las especificaciones técnicas del código QR de la factura», v0.5.0 (10-12-2025):
  URL de cotejo con nif, numserie, fecha (DD-MM-AAAA) e importe, con URL encoding UTF-8.
  El QR se genera con nivel M de corrección de errores y mide entre 30x30 y 40x40 mm.

Calculadora en línea (sin enviar datos): https://cirameva.com/software/verifactu/
Licencia MIT. Sin dependencias: solo la biblioteca estándar de Python 3.
"""
import hashlib
from urllib.parse import quote_plus

ALTA = ["IDEmisorFactura", "NumSerieFactura", "FechaExpedicionFactura", "TipoFactura",
        "CuotaTotal", "ImporteTotal", "Huella", "FechaHoraHusoGenRegistro"]
ANULACION = ["IDEmisorFacturaAnulada", "NumSerieFacturaAnulada", "FechaExpedicionFacturaAnulada",
             "Huella", "FechaHoraHusoGenRegistro"]


def _cadena(campos, valores):
    return "&".join(f"{c}={str(valores.get(c) or '').strip()}" for c in campos)


def _sha256(cadena):
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest().upper()


def cadena_alta(**v):
    """Cadena del registro de alta. Claves: los nombres de ALTA (Huella = huella del registro anterior o '')."""
    return _cadena(ALTA, v)


def cadena_anulacion(**v):
    """Cadena del registro de anulación. Claves: los nombres de ANULACION."""
    return _cadena(ANULACION, v)


def huella_alta(**v):
    return _sha256(cadena_alta(**v))


def huella_anulacion(**v):
    return _sha256(cadena_anulacion(**v))


def url_qr(nif, numserie, fecha, importe, verifactu=True, pruebas=False):
    """URL que va dentro del QR. verifactu=False -> ValidarQRNoVerifactu; pruebas=True -> entorno de pruebas externas."""
    base = "https://prewww2.aeat.es" if pruebas else "https://www2.agenciatributaria.gob.es"
    servicio = "ValidarQR" if verifactu else "ValidarQRNoVerifactu"
    par = [("nif", nif), ("numserie", numserie), ("fecha", fecha), ("importe", importe)]
    return f"{base}/wlpl/TIKE-CONT/{servicio}?" + "&".join(f"{k}={quote_plus(str(x).strip(), safe='', encoding='utf-8')}" for k, x in par)
