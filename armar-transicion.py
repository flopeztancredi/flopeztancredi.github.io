#!/usr/bin/env python3
"""Arma el sitio de transicion de flopeztancredi.github.io.

Los apuntes se mudaron a fiuba-resumenes.github.io, pero las notas y los
resaltados de cada lector viven en el localStorage del origen viejo. Este
sitio mantiene los apuntes viejos funcionando con una banda arriba que
explica la mudanza y pide sincronizar (o exportar) antes de pasarse, y
reemplaza cada service worker por uno que se desinstala y borra su cache,
asi nadie queda pegado a una copia vieja.

Uso: python3 armar.py <repo fiuba-resumenes.github.io> <salida>
"""
import re
import shutil
import sys
from pathlib import Path

NUEVO = "https://fiuba-resumenes.github.io"
MATERIAS = ["redes", "empresas-de-base-tecnologica",
            "empresas-de-base-tecnologica-2", "ciencia-de-datos"]
STUBS = ["ebt", "docs"]

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

PORTADA = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>FIUBA Resúmenes se mudó</title>
<link rel="canonical" href="{NUEVO}/">
<meta http-equiv="refresh" content="0; url={NUEVO}/">
<meta name="robots" content="noindex">
</head>
<body>
<p>Los apuntes ahora viven en <a href="{NUEVO}/">fiuba-resumenes.github.io</a>.</p>
</body>
</html>
"""


def main(repo: Path, salida: Path) -> int:
    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir(parents=True)
    (salida / ".nojekyll").write_text("")
    (salida / "index.html").write_text(PORTADA, encoding="utf-8")
    for m in MATERIAS:
        shutil.copytree(repo / m, salida / m)
        pagina = salida / m / "index.html"
        doc = pagina.read_text(encoding="utf-8")
        banda = BANDA.format(nuevo=f"{NUEVO}/{m}/", nuevo_corto=f"fiuba-resumenes.github.io/{m}")
        doc, n = re.subn(r"(<body[^>]*>)", lambda mm: mm.group(1) + banda, doc, count=1)
        if not n:
            print(f"!! {m}: no se encontro <body>", file=sys.stderr)
            return 1
        # sin manifest: no tiene sentido instalar la copia vieja
        doc = re.sub(r'\s*<link rel="manifest"[^>]*>', "", doc)
        pagina.write_text(doc, encoding="utf-8")
        (salida / m / "sw.js").write_text(SW_ADIOS, encoding="utf-8")
        for sobra in ("manifest.webmanifest",):
            (salida / m / sobra).unlink(missing_ok=True)
    for s in STUBS:
        shutil.copytree(repo / s, salida / s)
    print(f"listo: {salida} ({len(MATERIAS)} apuntes con banda, {len(STUBS)} stubs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
