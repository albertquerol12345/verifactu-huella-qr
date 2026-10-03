# verifactu-huella-qr

Huella (hash) SHA-256 de los registros de facturación VERI*FACTU, URL del QR tributario y XML de los registros (alta y anulación) en **Python** y **JavaScript**, probados con los ejemplos oficiales de la AEAT y validados contra sus esquemas XSD.

- Calculadora en línea, sin enviar datos: **https://cirameva.com/software/verifactu/**
- Sin dependencias: biblioteca estándar de Python 3 y Web Crypto (navegador o Node 18 o superior).
- Licencia MIT.

## Plazos

Según el Real Decreto-ley 15/2025 y la [nota de la AEAT](https://sede.agenciatributaria.gob.es/Sede/iva/sistemas-informaticos-facturacion-verifactu/nota-informativa-ampliacion-plazo-adaptacion-facturacion.html):

- Quien presenta el Impuesto sobre Sociedades tiene que tener el programa de facturación adaptado antes del **1 de enero de 2027**.
- El resto de obligados, antes del **1 de julio de 2027**.

## Python

```python
from verifactu_huella import huella_alta, huella_anulacion, url_qr

h1 = huella_alta(IDEmisorFactura="89890001K", NumSerieFactura="12345678/G33",
                 FechaExpedicionFactura="01-01-2024", TipoFactura="F1", CuotaTotal="12.35",
                 ImporteTotal="123.45", Huella="", FechaHoraHusoGenRegistro="2024-01-01T19:20:30+01:00")
# 3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60

url = url_qr("89890001K", "12345678&G33", "01-01-2024", "241.4", verifactu=True, pruebas=True)
# https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR?nif=89890001K&numserie=12345678%26G33&fecha=01-01-2024&importe=241.4
```

## JavaScript (navegador o Node)

```js
const vf = require("./verifactu.js");
const r = await vf.huella("alta", { IDEmisorFactura: "89890001K", NumSerieFactura: "12345678/G33",
  FechaExpedicionFactura: "01-01-2024", TipoFactura: "F1", CuotaTotal: "12.35", ImporteTotal: "123.45",
  Huella: "", FechaHoraHusoGenRegistro: "2024-01-01T19:20:30+01:00" });
// r.cadena = "IDEmisorFactura=89890001K&NumSerieFactura=12345678/G33&...", r.huella = "3C464DAF..."
```

Para dibujar el QR, `verifactu.js` usa la biblioteca [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) (MIT) con nivel M de corrección de errores: `svgQR(url, 35)` devuelve un SVG de 35 × 35 mm.

## XML de los registros (Python)

`verifactu_xml.py` monta `RegFactuSistemaFacturacion` con registros de alta (F1 o F2, IVA en régimen general con uno o varios tipos) y de anulación, calcula la huella encadenada y valida el resultado contra `xsd/SuministroLR.xsd`:

```python
from verifactu_xml import registro_alta, documento, validar

reg, huella = registro_alta("89890001K", "EMISOR EJEMPLO SL", "12345678/G33", "01-01-2024", "Servicios de ejemplo",
                            [("21.00", "111.10", "12.35")], sistema, "2024-01-01T19:20:30+01:00",
                            destinatario=("CLIENTE EJEMPLO SL", "B12345674"))
xml = documento("89890001K", "EMISOR EJEMPLO SL", [reg])
assert validar(xml) == []
```

`test_xml.py` construye la cadena alta → alta → anulación con los datos de los ejemplos de la AEAT, comprueba las 3 huellas oficiales y valida el XML (resultado en `ejemplo_RegFactuSistemaFacturacion.xml`). La carpeta `xsd/` copia los esquemas que publica la AEAT (descargados el 3-oct-2026) y el de XML-DSig del W3C; lo único cambiado es la ruta local del xmldsig.

## Puente para Access, Excel con VBA u otros programas antiguos

`verifactu_cli.py` sirve para programas que no calculan SHA-256 ni generan XML por sí mismos. El programa exporta sus facturas nuevas a un CSV y el script devuelve otro CSV con la huella encadenada, la URL del QR y los totales, además del XML de los registros validado contra el XSD. La cadena se guarda en un JSON entre ejecuciones.

```
python3 verifactu_cli.py nuevas.csv resultado.csv --cadena cadena.json --xml registros.xml --sistema sistema.json [--pruebas]
```

Desde VBA: `Shell "python verifactu_cli.py C:\fact\nuevas.csv C:\fact\resultado.csv --cadena C:\fact\cadena.json --xml C:\fact\registros.xml --sistema C:\fact\sistema.json", vbHide`. Ejemplo de entrada en `ejemplo_cli/`; prueba en `test_cli.py`.

## Pruebas

```
python3 test_verifactu.py
node test_verifactu.js
python3 test_xml.py      # requiere lxml
python3 test_cli.py      # requiere lxml
```

`vectores_aeat.json` trae los 3 ejemplos de huella de la especificación (primer registro, alta encadenada y anulación) y las URL de ejemplo del documento del QR.

## Reglas que aplica

- **Alta:** IDEmisorFactura, NumSerieFactura, FechaExpedicionFactura, TipoFactura, CuotaTotal, ImporteTotal, Huella (del registro anterior) y FechaHoraHusoGenRegistro.
- **Anulación:** IDEmisorFacturaAnulada, NumSerieFacturaAnulada, FechaExpedicionFacturaAnulada, Huella y FechaHoraHusoGenRegistro.
- **Formato de la cadena:** `nombre=valor` unidos con `&`, sin espacios al inicio ni al final de cada valor. Un campo vacío se escribe `nombre=`. La cadena se pasa a UTF-8 y se le aplica SHA-256; el resultado va en hexadecimal en mayúsculas.
- **QR:** la URL de cotejo lleva `nif`, `numserie`, `fecha` (DD-MM-AAAA) e `importe`, con URL encoding en UTF-8. El código va con nivel M y mide entre 30 × 30 y 40 × 40 mm, con «QR tributario:» encima. En VERI*FACTU lleva debajo «Factura verificable en la sede electrónica de la AEAT» o «VERI*FACTU».

Fuentes: AEAT, [especificaciones de la huella, v0.1.2](https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Veri-Factu_especificaciones_huella_hash_registros.pdf) y [especificaciones del QR, v0.5.0](https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/DetalleEspecificacTecnCodigoQRfactura.pdf).

## Lo que no hace

No firma los registros (modo No VERI*FACTU), no lleva el registro de eventos y no los envía al servicio web de la AEAT, porque eso necesita tu certificado electrónico. El XML cubre el caso común; las rectificativas, las operaciones exentas o no sujetas, el recargo de equivalencia y la facturación por terceros hay que añadirlas en `detalle`. Si necesitas el módulo completo dentro de tu programa de facturación, en Python, PHP, Java, .NET o Node, con pruebas en el entorno de la AEAT, lo hacemos en marca blanca: https://cirameva.com/software/modulo-verifactu/

Herramienta orientativa: no sustituye a las pruebas en el entorno de pruebas externas de la AEAT.
