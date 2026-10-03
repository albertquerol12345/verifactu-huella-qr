// Pruebas con los ejemplos oficiales de la AEAT. Ejecutar: node test_verifactu.js (Node 18 o superior)
const assert = require("assert");
const V = require("./vectores_aeat.json");
const vf = require("./verifactu.js");
(async () => {
  for (const c of V.huella) {
    const d = c.tipo === "alta" ? c.datos : { IDEmisorFactura: c.datos.IDEmisorFacturaAnulada, NumSerieFactura: c.datos.NumSerieFacturaAnulada, FechaExpedicionFactura: c.datos.FechaExpedicionFacturaAnulada, Huella: c.datos.Huella, FechaHoraHusoGenRegistro: c.datos.FechaHoraHusoGenRegistro };
    const r = await vf.huella(c.tipo, d);
    assert.strictEqual(r.huella, c.esperado, c.nombre); console.log("OK", c.nombre, r.huella);
  }
  for (const c of V.qr) {
    const u = vf.urlQR({ nif: c.datos.nif, numserie: c.datos.numserie, fecha: c.datos.fecha, importe: c.datos.importe, verificable: c.datos.verifactu, entorno: c.datos.pruebas ? "pruebas" : "produccion" });
    assert.strictEqual(u, c.esperado, c.nombre); console.log("OK", c.nombre);
  }
  console.log("Todas las pruebas pasan.");
})().catch(e => { console.error(e.message); process.exit(1); });
