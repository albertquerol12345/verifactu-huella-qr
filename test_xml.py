"""Construye una cadena alta → alta → anulación con los datos de los ejemplos de la AEAT, comprueba que las huellas
coinciden con las oficiales y valida el XML contra los XSD de la AEAT. Ejecutar: python3 test_xml.py (requiere lxml)."""
from verifactu_xml import registro_alta, registro_anulacion, documento, validar

SIS = {"NombreRazon": "EMPRESA DE SOFTWARE EJEMPLO SL", "NIF": "89890001K", "NombreSistemaInformatico": "FACTURADOR",
       "IdSistemaInformatico": "01", "Version": "1.0.0", "NumeroInstalacion": "1",
       "TipoUsoPosibleSoloVerifactu": "S", "TipoUsoPosibleMultiOT": "N", "IndicadorMultiplesOT": "N"}
r1, h1 = registro_alta("89890001K", "EMISOR EJEMPLO SL", "12345678/G33", "01-01-2024", "Servicios de ejemplo",
                       [("21.00", "111.10", "12.35")], SIS, "2024-01-01T19:20:30+01:00", destinatario=("CLIENTE EJEMPLO SL", "B12345674"))
assert h1 == "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60", h1
ant = {"IDEmisorFactura": "89890001K", "NumSerieFactura": "12345678/G33", "FechaExpedicionFactura": "01-01-2024", "Huella": h1}
r2, h2 = registro_alta("89890001K", "EMISOR EJEMPLO SL", "12345679/G34", "01-01-2024", "Servicios de ejemplo",
                       [("21.00", "111.10", "12.35")], SIS, "2024-01-01T19:20:35+01:00", anterior=ant, destinatario=("CLIENTE EJEMPLO SL", "B12345674"))
assert h2 == "F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97", h2
ant2 = {"IDEmisorFactura": "89890001K", "NumSerieFactura": "12345679/G34", "FechaExpedicionFactura": "01-01-2024", "Huella": h2}
r3, h3 = registro_anulacion("89890001K", "12345679/G34", "01-01-2024", SIS, "2024-01-01T19:20:40+01:00", ant2)
assert h3 == "177547C0D57AC74748561D054A9CEC14B4C4EA23D1BEFD6F2E69E3A388F90C68", h3
xml = documento("89890001K", "EMISOR EJEMPLO SL", [r1, r2, r3])
err = validar(xml)
assert not err, err
open("ejemplo_RegFactuSistemaFacturacion.xml", "w", encoding="utf-8").write(xml)
print("OK: 3 huellas oficiales y XML válido contra SuministroLR.xsd ->", "ejemplo_RegFactuSistemaFacturacion.xml")
