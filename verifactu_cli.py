"""Puente VERI*FACTU para programas que no pueden calcularlo por sí mismos (Access, Excel con VBA, FileMaker, programas antiguos).

El programa exporta sus facturas nuevas a un CSV; este script calcula la huella encadenada, la URL del QR y el XML
de los registros, y deja el resultado en otro CSV que el programa vuelve a importar. La cadena (último registro) se
guarda en un fichero JSON para continuar en la siguiente ejecución.

Uso:
  python3 verifactu_cli.py entrada.csv salida.csv --cadena cadena.json --xml registros.xml --sistema sistema.json [--pruebas]
Desde VBA (Access o Excel):
  Shell "python verifactu_cli.py C:\\fact\\nuevas.csv C:\\fact\\resultado.csv --cadena C:\\fact\\cadena.json --xml C:\\fact\\registros.xml --sistema C:\\fact\\sistema.json", vbHide

Columnas de entrada (separador «;», UTF-8): nif_emisor; nombre_emisor; num_serie; fecha (DD-MM-AAAA); tipo (F1 o F2);
descripcion; tipo_iva; base; cuota; nif_destinatario; nombre_destinatario; fecha_hora_huso (opcional; si falta, la hora actual).
Columnas de salida: las de entrada + cuota_total; importe_total; huella; url_qr.
No firma ni envía a la AEAT. Licencia MIT.
"""
import argparse, csv, json
from datetime import datetime
from pathlib import Path
from verifactu_huella import url_qr
from verifactu_xml import registro_alta, documento, validar


def ahora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("entrada"); ap.add_argument("salida")
    ap.add_argument("--cadena", required=True, help="JSON con el último registro (se crea si no existe)")
    ap.add_argument("--xml", required=True); ap.add_argument("--sistema", required=True, help="JSON con los datos de SistemaInformatico")
    ap.add_argument("--pruebas", action="store_true", help="URL del QR del entorno de pruebas de la AEAT")
    a = ap.parse_args(argv)
    sistema = json.loads(Path(a.sistema).read_text(encoding="utf-8"))
    pc = Path(a.cadena)
    anterior = json.loads(pc.read_text(encoding="utf-8")) if pc.exists() else None
    filas = list(csv.DictReader(open(a.entrada, encoding="utf-8-sig", newline=""), delimiter=";"))
    regs, salida = [], []
    for f in filas:
        fhh = (f.get("fecha_hora_huso") or "").strip() or ahora()
        dest = (f["nombre_destinatario"], f["nif_destinatario"]) if (f.get("nif_destinatario") or "").strip() else None
        xml, h = registro_alta(f["nif_emisor"], f["nombre_emisor"], f["num_serie"], f["fecha"], f["descripcion"],
                               [(f["tipo_iva"], f["base"], f["cuota"])], sistema, fhh, anterior=anterior,
                               tipo_factura=(f.get("tipo") or "F1").strip(), destinatario=dest)
        cuota = f"{float(f['cuota']):.2f}"; total = f"{float(f['base']) + float(f['cuota']):.2f}"
        regs.append(xml)
        salida.append({**f, "fecha_hora_huso": fhh, "cuota_total": cuota, "importe_total": total, "huella": h,
                       "url_qr": url_qr(f["nif_emisor"], f["num_serie"], f["fecha"], total, verifactu=True, pruebas=a.pruebas)})
        anterior = {"IDEmisorFactura": f["nif_emisor"].strip(), "NumSerieFactura": f["num_serie"].strip(),
                    "FechaExpedicionFactura": f["fecha"].strip(), "Huella": h}
    if not filas:
        print("Sin facturas nuevas."); return 0
    doc = documento(filas[0]["nif_emisor"], filas[0]["nombre_emisor"], regs)
    err = validar(doc)
    if err:
        print("XML NO válido; no se guarda nada:", *err[:5], sep="\n"); return 1
    Path(a.xml).write_text(doc, encoding="utf-8")
    with open(a.salida, "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(salida[0].keys()), delimiter=";"); w.writeheader(); w.writerows(salida)
    pc.write_text(json.dumps(anterior, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(salida)} registros; última huella {anterior['Huella']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
