/* CIRAMEVA · huella (hash) y QR tributario VERI*FACTU en el navegador.
   Huella: «Detalle de las especificaciones técnicas para generación de la huella o hash de los registros de facturación», AEAT v0.1.2 (27-08-2024):
   campo=valor&campo=valor… (valores sin espacios al inicio y al final; campo vacío = «campo=»), UTF-8, SHA-256, hexadecimal en mayúsculas.
   QR: «Detalle de las especificaciones técnicas del código QR de la factura», AEAT v0.5.0 (10-12-2025) y Orden HAC/1177/2024 arts. 20-21:
   URL de cotejo con nif, numserie, fecha (DD-MM-AAAA) e importe, parámetros con URL encoding UTF-8, ISO/IEC 18004 nivel M, 30x30 a 40x40 mm.
   No se envía ni se guarda nada: todo se calcula en esta página. */
(function () {
  "use strict";
  var EJ = {
    c1: { tipo: "alta", IDEmisorFactura: "89890001K", NumSerieFactura: "12345678/G33", FechaExpedicionFactura: "01-01-2024", TipoFactura: "F1", CuotaTotal: "12.35", ImporteTotal: "123.45", Huella: "", FechaHoraHusoGenRegistro: "2024-01-01T19:20:30+01:00", esperado: "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60" },
    c2: { tipo: "alta", IDEmisorFactura: "89890001K", NumSerieFactura: "12345679/G34", FechaExpedicionFactura: "01-01-2024", TipoFactura: "F1", CuotaTotal: "12.35", ImporteTotal: "123.45", Huella: "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60", FechaHoraHusoGenRegistro: "2024-01-01T19:20:35+01:00", esperado: "F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97" },
    c3: { tipo: "anulacion", IDEmisorFactura: "89890001K", NumSerieFactura: "12345679/G34", FechaExpedicionFactura: "01-01-2024", Huella: "F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97", FechaHoraHusoGenRegistro: "2024-01-01T19:20:40+01:00", esperado: "177547C0D57AC74748561D054A9CEC14B4C4EA23D1BEFD6F2E69E3A388F90C68" }
  };
  var ORDEN = {
    alta: [["IDEmisorFactura", "IDEmisorFactura"], ["NumSerieFactura", "NumSerieFactura"], ["FechaExpedicionFactura", "FechaExpedicionFactura"], ["TipoFactura", "TipoFactura"], ["CuotaTotal", "CuotaTotal"], ["ImporteTotal", "ImporteTotal"], ["Huella", "Huella"], ["FechaHoraHusoGenRegistro", "FechaHoraHusoGenRegistro"]],
    anulacion: [["IDEmisorFacturaAnulada", "IDEmisorFactura"], ["NumSerieFacturaAnulada", "NumSerieFactura"], ["FechaExpedicionFacturaAnulada", "FechaExpedicionFactura"], ["Huella", "Huella"], ["FechaHoraHusoGenRegistro", "FechaHoraHusoGenRegistro"]]
  };
  function cadena(tipo, v) {
    return ORDEN[tipo].map(function (p) { return p[0] + "=" + String(v[p[1]] == null ? "" : v[p[1]]).trim(); }).join("&");
  }
  function sha256Hex(txt) {
    var bytes = new TextEncoder().encode(txt);
    return crypto.subtle.digest("SHA-256", bytes).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ("0" + b.toString(16)).slice(-2); }).join("").toUpperCase();
    });
  }
  function huella(tipo, v) { var c = cadena(tipo, v); return sha256Hex(c).then(function (h) { return { cadena: c, huella: h }; }); }
  // Validaciones de formato (diseño de registro y especificaciones del QR)
  var RX = {
    nif: /^[0-9A-Z]{9}$/,
    fecha: /^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$/,
    importe: /^-?\d{1,12}(\.\d{1,2})?$/,
    fhh: /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/,
    huella: /^([0-9A-F]{64})?$/,
    ascii: /^[\x20-\x7E]{1,60}$/
  };
  function avisos(tipo, v) {
    var a = [];
    if (!RX.nif.test(v.IDEmisorFactura.trim())) a.push("El NIF del emisor debe tener 9 caracteres (letras en mayúscula).");
    if (!RX.ascii.test(v.NumSerieFactura.trim())) a.push("La serie y número admite de 1 a 60 caracteres ASCII imprimibles (códigos 32 a 126): sin tildes ni «ñ».");
    if (!RX.fecha.test(v.FechaExpedicionFactura.trim())) a.push("La fecha de expedición va como DD-MM-AAAA (por ejemplo, 01-01-2024).");
    if (tipo === "alta") {
      if (!/^(F1|F2|F3|R1|R2|R3|R4|R5)$/.test(v.TipoFactura.trim())) a.push("Tipo de factura: F1, F2, F3 o R1 a R5.");
      if (!RX.importe.test(v.CuotaTotal.trim())) a.push("Cuota total: número con punto decimal y como mucho 2 decimales (12.35).");
      if (!RX.importe.test(v.ImporteTotal.trim())) a.push("Importe total: número con punto decimal y como mucho 2 decimales (123.45).");
    }
    if (!RX.huella.test(v.Huella.trim())) a.push("La huella anterior son 64 caracteres hexadecimales en mayúsculas, o vacía si es el primer registro del sistema.");
    if (!RX.fhh.test(v.FechaHoraHusoGenRegistro.trim())) a.push("Fecha, hora y huso: AAAA-MM-DDThh:mm:ss+hh:mm (por ejemplo, 2024-01-01T19:20:30+01:00).");
    return a;
  }
  function ahoraISO() {
    var d = new Date(), z = -d.getTimezoneOffset(), s = z >= 0 ? "+" : "-", p = function (n) { return ("0" + Math.floor(Math.abs(n))).slice(-2); };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) + "T" + p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds()) + s + p(z / 60) + ":" + p(z % 60);
  }
  // URL encoding en UTF-8 (también ! ' ( ) * y el espacio como «+»)
  function enc(s) { return encodeURIComponent(s).replace(/[!'()*]/g, function (c) { return "%" + c.charCodeAt(0).toString(16).toUpperCase(); }).replace(/%20/g, "+"); }
  function urlQR(o) {
    var base = (o.entorno === "pruebas" ? "https://prewww2.aeat.es" : "https://www2.agenciatributaria.gob.es") + "/wlpl/TIKE-CONT/" + (o.verificable ? "ValidarQR" : "ValidarQRNoVerifactu");
    return base + "?nif=" + enc(o.nif.trim()) + "&numserie=" + enc(o.numserie.trim()) + "&fecha=" + enc(o.fecha.trim()) + "&importe=" + enc(o.importe.trim());
  }
  function svgQR(texto, mm) {
    if (typeof qrcode !== "function") return "";
    var q = qrcode(0, "M"); q.addData(texto, "Byte"); q.make();
    var n = q.getModuleCount(), cell = 10, quiet = 4, tam = (n + 2 * quiet) * cell, d = "";
    for (var r = 0; r < n; r++) for (var c = 0; c < n; c++) if (q.isDark(r, c)) d += "M" + ((c + quiet) * cell) + "," + ((r + quiet) * cell) + "h" + cell + "v" + cell + "h-" + cell + "z";
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + tam + " " + tam + '" width="' + mm + 'mm" height="' + mm + 'mm" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path d="' + d + '" fill="#000"/></svg>';
  }
  if (typeof module !== "undefined" && module.exports) { module.exports = { cadena: cadena, huella: huella, avisos: avisos, urlQR: urlQR, svgQR: svgQR, EJ: EJ }; return; }

  function $(root, s) { return root.querySelector(s); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ---- calculadora de huella
  var H = document.getElementById("vf-huella");
  if (H) {
    var esperado = "";
    var campos = ["IDEmisorFactura", "NumSerieFactura", "FechaExpedicionFactura", "TipoFactura", "CuotaTotal", "ImporteTotal", "Huella", "FechaHoraHusoGenRegistro"];
    var tipoSel = $(H, "[name=tipo]");
    function leer() { var v = {}; campos.forEach(function (k) { var i = $(H, "[name=" + k + "]"); v[k] = i ? i.value : ""; }); return v; }
    function pintarTipo() { var an = tipoSel.value === "anulacion"; H.querySelectorAll(".solo-alta").forEach(function (el) { el.hidden = an; }); }
    function calcular() {
      var tipo = tipoSel.value, v = leer(), out = $(H, ".vf-out"), av = avisos(tipo, v);
      huella(tipo, v).then(function (r) {
        var ok = esperado ? (r.huella === esperado ? '<p class="vf-ok">Coincide con el resultado publicado por la AEAT para este ejemplo.</p>' : '<p class="vf-mal">No coincide con el resultado de la AEAT (' + esperado + ").</p>") : "";
        out.innerHTML = '<p class="vf-l">Cadena sobre la que se calcula la huella</p><code class="vf-code">' + esc(r.cadena) + "</code>" +
          '<p class="vf-l">Huella SHA-256 (hexadecimal en mayúsculas)</p><code class="vf-code vf-h">' + r.huella + "</code>" + ok +
          (av.length ? '<div class="box warn" style="margin-top:12px"><b>Revisa el formato:</b><ul>' + av.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "");
        out.dataset.h = r.huella;
      }).catch(function () { out.innerHTML = '<p class="box warn">Tu navegador no permite calcular SHA-256 aquí (hace falta HTTPS y un navegador actual).</p>'; });
    }
    H.addEventListener("input", function () { esperado = ""; calcular(); });
    tipoSel.addEventListener("change", function () { pintarTipo(); esperado = ""; calcular(); });
    H.querySelectorAll("[data-ej]").forEach(function (b) {
      b.addEventListener("click", function () {
        var ej = EJ[b.dataset.ej]; tipoSel.value = ej.tipo; pintarTipo();
        campos.forEach(function (k) { var i = $(H, "[name=" + k + "]"); if (i) i.value = ej[k] == null ? "" : ej[k]; });
        esperado = ej.esperado; calcular();
      });
    });
    $(H, ".vf-ahora").addEventListener("click", function () { $(H, "[name=FechaHoraHusoGenRegistro]").value = ahoraISO(); esperado = ""; calcular(); });
    $(H, ".vf-encadenar").addEventListener("click", function () {
      var h = $(H, ".vf-out").dataset.h; if (!h) return;
      $(H, "[name=Huella]").value = h; $(H, "[name=FechaHoraHusoGenRegistro]").value = ahoraISO(); esperado = ""; calcular();
    });
    pintarTipo(); calcular();
  }

  // ---- generador del QR tributario
  var Q = document.getElementById("vf-qr");
  if (Q) {
    function leerQ() {
      return { nif: $(Q, "[name=nif]").value, numserie: $(Q, "[name=numserie]").value, fecha: $(Q, "[name=fecha]").value, importe: $(Q, "[name=importe]").value,
               verificable: $(Q, "[name=modo]").value === "verifactu", entorno: $(Q, "[name=entorno]").value, mm: +$(Q, "[name=mm]").value || 35, frase: $(Q, "[name=frase]").value };
    }
    function pintarQ() {
      var o = leerQ(), u = urlQR(o), av = [];
      if (!RX.nif.test(o.nif.trim())) av.push("NIF: 9 caracteres, letras en mayúscula.");
      if (!RX.ascii.test(o.numserie.trim())) av.push("Serie y número: de 1 a 60 caracteres ASCII imprimibles (sin tildes ni «ñ»).");
      if (!RX.fecha.test(o.fecha.trim())) av.push("Fecha: DD-MM-AAAA.");
      if (!RX.importe.test(o.importe.trim())) av.push("Importe: hasta 12 cifras enteras, punto decimal y 2 decimales como mucho.");
      var svg = svgQR(u, o.mm);
      var pie = o.verificable ? (o.frase === "corta" ? "VERI*FACTU" : "Factura verificable en la sede electrónica de la AEAT") : "";
      $(Q, ".vf-qr-out").innerHTML = '<p class="vf-l">URL del QR</p><code class="vf-code">' + esc(u) + "</code>" +
        '<div class="vf-qr-fig"><p class="vf-qr-t">QR tributario:</p>' + (svg || '<p class="box warn">No se ha podido cargar el generador de QR.</p>') + (pie ? '<p class="vf-qr-t">' + esc(pie) + "</p>" : "") + "</div>" +
        (av.length ? '<div class="box warn"><b>Revisa el formato:</b><ul>' + av.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "");
      Q.dataset.svg = svg; Q.dataset.url = u;
    }
    Q.addEventListener("input", pintarQ); Q.addEventListener("change", pintarQ);
    $(Q, ".vf-svg").addEventListener("click", function () {
      if (!Q.dataset.svg) return;
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([Q.dataset.svg], { type: "image/svg+xml" })); a.download = "qr_verifactu.svg"; a.click();
    });
    $(Q, ".vf-copiar").addEventListener("click", function () { if (navigator.clipboard && Q.dataset.url) navigator.clipboard.writeText(Q.dataset.url); });
    pintarQ();
  }
})();
