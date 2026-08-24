#!/usr/bin/env python3
"""Agrega Aprendizaje Automatico y Sistemas Distribuidos al sitio de
transicion de flopeztancredi.github.io, ahora que se transfirieron al org
(fase D). Misma banda + SW de despedida que ya tienen redes/ebt/ebt2/cdd.
"""
import re
import shutil
from pathlib import Path

NUEVO = "https://fiuba-resumenes.github.io"
SITIO = Path("/tmp/claude-1000/-home-lopez-fiuba/eb21b154-fa73-47ec-84a0-01f625e1cd1b/scratchpad/transicion-live")
AA = Path("/home/lopez/fiuba/automatico")
SD = Path("/home/lopez/fiuba/distribuidos/apunte")

BANDA = """
<div id="mudanza" style="position:sticky;top:0;z-index:9999;padding:12px 18px;background:#fff3cd;color:#3b2f00;border-bottom:1px solid #e0c46b;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif">
  <b>Este apunte se mudó a</b> <a id="mudanza-link" href="{nuevo}" style="color:#3b2f00;font-weight:700">{nuevo_corto}</a>.
  Las notas y resaltados que hiciste acá quedan guardados solo en esta dirección vieja:
  antes de pasarte, apretá <b>Sincronizar</b> en el panel lateral (frase de 12 palabras) o exportá tus notas, y cargalas del otro lado.
</div>
<script>
  (function () {{
    var a = document.getElementById('mudanza-link');
    a.href = '{nuevo}' + location.hash;
  }})();
</script>
"""

SW_ADIOS = """// Service worker de despedida: borra el cache de este origen y se
// desinstala, para que el apunte viejo se cargue siempre de la red (con la
// banda de mudanza) y no de una copia guardada.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((ks) => Promise.all(ks.map((k) => caches.delete(k))))
    .then(() => self.registration.unregister())
    .then(() => self.clients.matchAll({ type: 'window' }))
    .then((cs) => cs.forEach((c) => c.navigate(c.url))));
});
"""


def banda_pagina(pagina: Path, nuevo: str, nuevo_corto: str) -> None:
    doc = pagina.read_text(encoding="utf-8")
    banda = BANDA.format(nuevo=nuevo, nuevo_corto=nuevo_corto)
    doc, n = re.subn(r"(<body[^>]*>)", lambda mm: mm.group(1) + banda, doc, count=1)
    if not n:
        raise SystemExit(f"!! {pagina}: no se encontro <body>")
    doc = re.sub(r'\s*<link rel="manifest"[^>]*>', "", doc)
    pagina.write_text(doc, encoding="utf-8")


def main() -> int:
    # --- Aprendizaje Automatico: repo -> flopeztancredi.github.io/aprendizaje-automatico/
    destino = SITIO / "aprendizaje-automatico"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    for nombre in ("index.html", "resumen.html", "resumen-analitico.html"):
        shutil.copyfile(AA / nombre, destino / nombre)
    banda_pagina(destino / "index.html", f"{NUEVO}/aprendizaje-automatico/",
                 "fiuba-resumenes.github.io/aprendizaje-automatico")
    banda_pagina(destino / "resumen.html", f"{NUEVO}/aprendizaje-automatico/",
                 "fiuba-resumenes.github.io/aprendizaje-automatico")
    (destino / "sw.js").write_text(SW_ADIOS, encoding="utf-8")
    print(f"listo: {destino} (2 paginas con banda, 1 stub sin tocar)")

    # --- Sistemas Distribuidos: repo -> flopeztancredi.github.io/sistemas-distribuidos/
    destino = SITIO / "sistemas-distribuidos"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    shutil.copyfile(SD / "index.html", destino / "index.html")
    banda_pagina(destino / "index.html", f"{NUEVO}/sistemas-distribuidos/",
                 "fiuba-resumenes.github.io/sistemas-distribuidos")
    (destino / "sw.js").write_text(SW_ADIOS, encoding="utf-8")

    resumen_destino = destino / "resumen"
    resumen_destino.mkdir()
    shutil.copyfile(SD / "resumen" / "index.html", resumen_destino / "index.html")
    banda_pagina(resumen_destino / "index.html", f"{NUEVO}/sistemas-distribuidos/resumen/",
                 "fiuba-resumenes.github.io/sistemas-distribuidos/resumen")
    (resumen_destino / "sw.js").write_text(SW_ADIOS, encoding="utf-8")
    print(f"listo: {destino} (2 paginas con banda + resumen/, cada una con su SW de despedida)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
