"""Pruebas con los ejemplos oficiales de la AEAT. Ejecutar: python3 test_verifactu.py"""
import json
from pathlib import Path
from verifactu_huella import huella_alta, huella_anulacion, url_qr

V = json.loads((Path(__file__).parent / "vectores_aeat.json").read_text(encoding="utf-8"))
for caso in V["huella"]:
    f = huella_alta if caso["tipo"] == "alta" else huella_anulacion
    obtenido = f(**caso["datos"])
    assert obtenido == caso["esperado"], (caso["nombre"], obtenido)
    print("OK", caso["nombre"], obtenido)
for caso in V["qr"]:
    obtenido = url_qr(**caso["datos"])
    assert obtenido == caso["esperado"], (caso["nombre"], obtenido)
    print("OK", caso["nombre"])
print("Todas las pruebas pasan.")
