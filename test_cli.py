"""Prueba del puente: 2 facturas con los datos de los ejemplos de la AEAT deben dar sus huellas oficiales, y una 3.ª
ejecución debe continuar la cadena. Ejecutar: python3 test_cli.py (requiere lxml)."""
import csv, json, tempfile
from pathlib import Path
from verifactu_cli import main

d = Path(tempfile.mkdtemp()); ej = Path(__file__).parent / "ejemplo_cli"
args = lambda e: [str(e), str(d / "res.csv"), "--cadena", str(d / "cadena.json"), "--xml", str(d / "reg.xml"), "--sistema", str(ej / "sistema.json"), "--pruebas"]
assert main(args(ej / "nuevas.csv")) == 0
r = list(csv.DictReader(open(d / "res.csv", encoding="utf-8"), delimiter=";"))
assert [x["huella"] for x in r] == ["3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60",
                                    "F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97"], r
assert r[0]["url_qr"] == "https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR?nif=89890001K&numserie=12345678%2FG33&fecha=01-01-2024&importe=123.45"
assert json.loads((d / "cadena.json").read_text())["Huella"].startswith("F7B94CFD")
(d / "otra.csv").write_text("nif_emisor;nombre_emisor;num_serie;fecha;tipo;descripcion;tipo_iva;base;cuota;nif_destinatario;nombre_destinatario;fecha_hora_huso\n"
                            "89890001K;EMISOR EJEMPLO SL;12345680/G35;02-01-2024;F2;Venta mostrador;21.00;10.00;2.10;;;2024-01-02T10:00:00+01:00\n", encoding="utf-8")
assert main(args(d / "otra.csv")) == 0
assert "<sf:RegistroAnterior><sf:IDEmisorFactura>89890001K</sf:IDEmisorFactura><sf:NumSerieFactura>12345679/G34" in (d / "reg.xml").read_text()
print("OK: puente CSV → huellas oficiales, URL del QR, XML válido y cadena continuada entre ejecuciones")
