"""Vista previa al compartir (Instagram, WhatsApp...) e icono de pestaña para todas las páginas.

1. Hace una captura de la parte de arriba de cada página (1200x630) y la guarda en og/<carpeta>.jpg.
2. Añade (o actualiza) en el <head> de cada página las etiquetas og:/twitter: y el icono.
3. Crea el icono (favicon.ico, assets/icono.png, assets/icono-apple.png) a partir del logo.

Uso:  python herramientas/vista-previa.py              (todas las páginas)
      python herramientas/vista-previa.py lm22-xxx     (solo las carpetas indicadas)
Vuelve a ejecutarlo después de generar-lm.py o al crear una página nueva.
Necesita Microsoft Edge (o Chrome) y Pillow.
"""
import html, http.server, os, re, shutil, subprocess, sys, tempfile, threading
from functools import partial
from PIL import Image, ImageDraw

DOMINIO = "https://edurehab.onrender.com"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVEGADORES = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
EXCLUIR = {"indice-paginas-er", "herramientas", "assets", "og"}   # el índice privado no lleva imagen pública
INICIO, FIN = "<!-- vista-previa -->", "<!-- /vista-previa -->"


def paginas(solo):
    """(carpeta, ruta del index.html); la portada es la carpeta ''."""
    out = [("", os.path.join(RAIZ, "index.html"))]
    for d in sorted(os.listdir(RAIZ)):
        f = os.path.join(RAIZ, d, "index.html")
        if os.path.isfile(f) and not d.startswith(".") and d not in EXCLUIR:
            out.append((d, f))
    return [p for p in out if not solo or p[0] in solo]


def iconos():
    logo = Image.open(os.path.join(RAIZ, "assets", "logo-evorehab.png")).convert("RGBA")
    def cuadrado(lado):
        im = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, lado - 1, lado - 1), radius=lado // 5, fill=(255, 255, 255, 255))
        l = logo.copy(); l.thumbnail((int(lado * .8), int(lado * .8)), Image.LANCZOS)
        im.alpha_composite(l, ((lado - l.width) // 2, (lado - l.height) // 2))
        return im
    cuadrado(192).save(os.path.join(RAIZ, "assets", "icono.png"), optimize=True)
    cuadrado(180).save(os.path.join(RAIZ, "assets", "icono-apple.png"), optimize=True)
    cuadrado(48).save(os.path.join(RAIZ, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def capturas(lista):
    nav = next((n for n in NAVEGADORES if os.path.isfile(n)), None)
    if not nav:
        sys.exit("No encuentro Edge ni Chrome para hacer las capturas.")
    os.makedirs(os.path.join(RAIZ, "og"), exist_ok=True)
    # La página se abre dentro de un marco desde una página auxiliar que antes marca las cookies como respondidas,
    # para que el aviso de cookies no salga en la captura.
    aux = "__vista-previa.html"
    with open(os.path.join(RAIZ, aux), "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html><html><body style="margin:0;overflow:hidden"><script>'
                'localStorage.setItem("evo-cookies","esenciales");'
                'var i=document.createElement("iframe");i.src=decodeURIComponent(location.hash.slice(1));'
                'i.style.cssText="width:1200px;height:630px;border:0;display:block";document.body.appendChild(i);'
                '</script></body></html>')
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), partial(Silencioso, directory=RAIZ))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    perfil = tempfile.mkdtemp()
    try:
        for carpeta, _ in lista:
            url = f"http://127.0.0.1:{srv.server_port}/{aux}#/{carpeta + '/' if carpeta else ''}"
            png = os.path.join(perfil, "c.png")
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            "--window-size=1200,630", "--virtual-time-budget=30000", f"--user-data-dir={perfil}",
                            f"--screenshot={png}", url], check=True, capture_output=True, timeout=120)
            nombre = (carpeta or "inicio") + ".jpg"
            Image.open(png).convert("RGB").crop((0, 0, 1200, 630)).save(os.path.join(RAIZ, "og", nombre), quality=82, optimize=True)
            print("captura", nombre)
    finally:
        srv.shutdown()
        os.remove(os.path.join(RAIZ, aux))
        shutil.rmtree(perfil, ignore_errors=True)


def etiquetas(carpeta, ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        doc = f.read()
    doc = re.sub(r"\n?\s*" + re.escape(INICIO) + r".*?" + re.escape(FIN), "", doc, flags=re.S)
    m = re.search(r"<title>(.*?)</title>", doc, re.S)
    titulo = html.unescape(m.group(1).strip()) if m else "EVOREHAB"
    m = re.search(r'<meta\s+name="description"\s+content="(.*?)"', doc, re.S)
    desc = html.unescape(m.group(1).strip()) if m else "Readaptación online de rodilla con @edu.rehab"
    url = f"{DOMINIO}/{carpeta + '/' if carpeta else ''}"
    img = f"{DOMINIO}/og/{carpeta or 'inicio'}.jpg"
    e = lambda s: html.escape(s, quote=True)
    bloque = f"""  {INICIO}
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" href="/assets/icono.png" />
  <link rel="apple-touch-icon" href="/assets/icono-apple.png" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="EVOREHAB" />
  <meta property="og:title" content="{e(titulo)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{img}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  {FIN}"""
    doc = re.sub(r"(<title>.*?</title>)", lambda m: m.group(1) + "\n" + bloque, doc, count=1, flags=re.S)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(doc)


if __name__ == "__main__":
    lista = paginas(set(sys.argv[1:]))
    iconos()
    for c, r in lista:
        etiquetas(c, r)
    capturas(lista)
    print(len(lista), "páginas listas")
