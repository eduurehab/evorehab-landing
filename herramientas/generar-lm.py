"""Convierte los PDF de lead magnet en páginas web (lmN-slug/index.html)."""
import os, re, sys, html, json, urllib.request, io, urllib.parse
import pymupdf
from PIL import Image

ORIGEN = r"C:/Users/Usuario/Desktop/@edu.rehab/1. Instagram/Lead Magnets, Regalos/Nuevos/"
DESTINO = os.environ.get("LM_DESTINO", r"C:/Users/Usuario/Desktop/Proyectos CLAUDE/Landing ER (post-samu)/")

# num, slug, pdf, kicker
LMS = [
    (1, "bienvenida-eliminar-dolor", "LM - Bienvenida (1) - Eliminar dolor y pinchazos.pdf", "Guía de bienvenida"),
    (2, "bienvenida-gym-con-dolor", "LM - Bienvenida (2) - Entrenar en Gym con dolor de forma segura.pdf", "Guía de bienvenida"),
    (3, "bienvenida-cirugia-5-fases", "LM - Bienvenida (3) - Cirugía 5 fases.pdf", "Guía de bienvenida"),
    (4, "guia-definitiva-dolor", "LM FIJADO. Guía definitiva del dolor.pdf", "Guía definitiva"),
    (5, "tabla-autoevaluacion-dolor", "LM Tabla autoevaluación dolor.pdf", "Herramienta"),
    (6, "sesion-iso-exc-dolor-rodilla", "LM Sesión ISO + EXC dolor rodilla.pdf", "Sesión de ejercicios"),
    (7, "tratamiento-condromalacias", "LM - Diferencias tratamiento condromalacias.pdf", "Guía"),
    (9, "impacta-sin-miedo", "LM - Impacta sin miedo - Saltar y correr condromalacia.pdf", "Guía"),
    (10, "antes-del-bisturi", "LM - Antes del bisturí. Qué hacer antes para acelerar el proceso después.pdf", "Guía"),
    (11, "5-fases-lca", "LM - EVOREHAB-5-fases-LCA.pdf", "Guía"),
    (12, "tests-lca", "LM Tests a realizar tras una reconstrucción de LCA.pdf", "Guía de tests"),
    (13, "artrofibrosis-adherencias", "LM Artrofibrosis y adherencias.pdf", "Guía"),
    (14, "de-la-camilla-al-gimnasio", "LM - De la camilla al gimnasio.pdf", "Guía"),
    (15, "progresion-caco-carrera", "LM - Progresión CaCo carrera.pdf", "Progresión"),
    (16, "checklist-senales-progreso", "LM Checklist de señales de progreso.pdf", "Checklist"),
    (17, "20-preguntas-plan-optimo", "LM 20 preguntas plan óptimo.pdf", "Cuestionario"),
    (18, "3-claves-masa-muscular", "LM Las 3 claves para ganar masa muscular.pdf", "Guía"),
    (19, "errores-que-cometi", "LM Errores que cometí en mis lesiones y que tú puedes evitar.pdf", "Guía"),
    (23, "test4preguntas", "LM arbol decision 4 preguntas.pdf", "Test"),
]

REGIONES = {23: {2: [(15, 805)]}, 7: {3: [(295, 695)]}, 15: {0: [(420, 650)], 2: [(90, 715)]}}
# Resaltado en cian dentro del título (por número de LM)
DESTACAR = {1: "eliminar los pinchazos", 2: "de forma segura", 3: "volver a rendir", 4: "del dolor", 5: "autoevaluación", 6: "Elimina tu dolor de rodilla",
            7: "rotuliana vs femoral", 9: "sin miedo", 10: "bisturí", 11: "volver a tu deporte", 12: "reconstrucción de LCA", 13: "artrofibrosis",
            14: "gimnasio", 15: "retomar la carrera", 16: "señales de progreso", 17: "preguntas", 18: "masa muscular", 19: "mis lesiones pasadas", 23: "decisión"}
# Títulos en cápsula que en el PDF son imagen: se pasan a texto real (HTML), en orden de aparición
CAPSULAS = {
    1: ["La falsa solución que está <span class=\"cy\">debilitando</span> tu rodilla", "El camino real para <span class=\"cy\">recuperar tu rodilla</span>", "Tu punto de partida <span class=\"cy\">hoy mismo</span>"],
    2: ["Los errores que hacen que <span class=\"cy\">no te quites el dolor</span> ni la lesión", "Los 3 pilares de tu entrenamiento", "Lo más importante de todo"],
    3: ["Los problemas de hacer una <span class=\"cy\">mala rehab</span>", "El mapa de las 5 fases",
        "Fase 1 · Movilidad base, musculatura base, entrenamiento cruzado y recuperación de la marcha <small>Semanas 1 a 6, aprox.</small>",
        "Fase 2 · Movilidad avanzada, reducción de asimetrías y ganancia de masa muscular",
        "Fase 3 · Carrera, pliometría, potencia y cambios de dirección (COD)",
        "Fase 4 · Maximización del rendimiento y contexto deportivo real",
        "Fase 5 · Evolución y prevención", "Extra · Preoperatorio", "No te olvides de <span class=\"cy\">esto</span>"],
}
CTA = "!Quiero agendar una reunión con Edu y contarle mi caso"
CAPSULAS[9] = ["~Isometría en ángulos seguros", "~Fuerza excéntrica controlada", "~Pliometría extensiva de bajo impacto", CTA]
CAPSULAS[10] = ["~Extensión máxima (0°) y flexión de al menos 110-120°", "~Ausencia de inflamación activa", "~Capacidad de carga con ejercicios clave", "~Déficit de fuerza entre piernas menos al 15-10%", CTA]
KICKERS_11 = {"1": "FASE 1 · POSTOPERATORIO O CONSERVADOR", "2": "FASE 2 · FUERZA Y SIMETRÍAS", "3": "FASE 3 · IMPACTOS, CARRERA Y CAMBIOS DE DIRECCIÓN", "4": "FASE 4 · RENDIMIENTO EN TU DEPORTE", "5": "FASE 5 · PREVENCIÓN DE POR VIDA"}
SIN_CIERRE = {1, 2, 3}   # sin botón de WhatsApp: el texto del PDF ya manda al chat de Instagram
SIN_PORTADA = {15: ["Cómo retomar la carrera", "Método CaCo (caminar-correr)"], 16: ["Checklist de señales de progreso"]}
CABECERA = re.compile(r"^(pregunta\s+s[ií]\s+no|evorehab\s*·\s*las 5 fases.*|.*edurehab.*c[oó]mo retomar.*|puedes preguntarme lo que quieras.*|pregunta\s+s[ií]\s+no|siguiente p[aá]gina|[↓⬇⬇️]+|programa\s*evorehab|eduardo est[ée]vez|@edu\.rehab|sigue leyendo( las siguientes p[aá]ginas)?|evorehab)$", re.I)
AUTOR = re.compile(r"(^lesiones de rodilla$|eduardo est[ée]vez|@edu\.rehab|graduado en|posgrado|ceo programa|especialista en readaptaci|programa\s*evorehab|ciencias de la (a\.f|actividad)|experto universitario|m[úu]ltiples formaciones)", re.I)
BULLETS = set("⬜⬛•·▪●○◦■□☐☑✓✔✅❌-–—➤➔►▶→") | {chr(c) for c in range(0xE000, 0xF900)}
CHECK = set("⬜□☐☑✓✔")


def acento(col):
    r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
    return max(r, g, b) - min(r, g, b) > 70 and max(r, g, b) > 90


def esc(t):
    return html.escape(t, quote=False)


def yt_id(u):
    m = re.search(r"(?:shorts/|youtu\.be/|v=|embed/)([\w-]{11})", u or "")
    return m.group(1) if m else None


def segmentar(page, doc_tipo_portada):
    """Devuelve elementos de la página en orden: dict(tipo, y, ...)."""
    pw, ph = page.rect.width, page.rect.height
    links = page.get_links()
    d = page.get_text("dict")
    lineas = []
    vistos = set()
    for bi, b in enumerate(d["blocks"]):
        if b["type"] != 0:
            continue
        bmax = max((ln["bbox"][2] - ln["bbox"][0]) for ln in b["lines"])
        for l in b["lines"]:
            spans = [s for s in l["spans"] if s["text"].strip() != "" or s["text"] == " "]
            for s in spans:
                s["text"] = re.sub(r"[-–_]{5,}", " ", s["text"])
            t = "".join(s["text"] for s in spans).strip()
            if not t:
                continue
            clave = (t, round(l["bbox"][0] / 3), round(l["bbox"][1] / 3))
            if clave in vistos:
                continue
            vistos.add(clave)
            for s in spans:
                s["href"] = None
                sr = pymupdf.Rect(s["bbox"])
                for k in links:
                    if k.get("uri") and sr.intersects(pymupdf.Rect(k["from"])):
                        inter = sr & pymupdf.Rect(k["from"])
                        if inter.get_area() > 0.3 * sr.get_area():
                            s["href"] = k["uri"]
            lineas.append({"bbox": l["bbox"], "spans": spans, "text": t, "size": max(s["size"] for s in spans), "blk": (page.number, bi), "bmax": bmax})
    pts = []
    try:
        for dr in page.get_drawings():
            r = dr["rect"]
            if dr.get("fill") and 2 <= r.width <= 9 and 2 <= r.height <= 9 and abs(r.width - r.height) < 3 and dr["fill"] != (1.0, 1.0, 1.0):
                pts.append(r)
    except Exception:
        pass
    for l in lineas:
        bx = l["bbox"]
        for r in pts:
            cy = (r.y0 + r.y1) / 2
            if bx[1] - 2 <= cy <= bx[3] + 2 and bx[0] - 28 <= r.x1 <= bx[0] + 2:
                l["vbullet"] = True
                break
    return lineas, links


def estilo_span(s):
    f = s["font"].lower()
    neg = bool(s["flags"] & 16) or "bold" in f or "black" in f or "heavy" in f
    cur = bool(s["flags"] & 2) or "italic" in f or "oblique" in f
    return neg, cur, acento(s["color"])


def html_spans(spans):
    partes = []
    prev = None
    for s in spans:
        neg, cur, ac = estilo_span(s)
        clave = (neg, cur, ac, s["href"])
        txt = s["text"]
        if prev and prev[0] == clave:
            prev[1].append(txt)
        else:
            prev = [clave, [txt]]
            partes.append(prev)
    out = ""
    for (neg, cur, ac, href), ts in partes:
        t = esc("".join(ts))
        if not t.strip():
            out += t
            continue
        if neg: t = f"<strong>{t}</strong>"
        if cur: t = f"<em>{t}</em>"
        if ac: t = f'<span class="ac">{t}</span>'
        if href: t = f'<a href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">{t}</a>'
        out += t
    return out


def parrafos(lineas, ph=842):
    anchos = sorted(l["bbox"][2] for l in lineas if len(l["text"]) > 45)
    der = anchos[int(len(anchos) * 0.85)] if anchos else 0
    """Agrupa líneas en párrafos/viñetas/títulos."""
    lineas = sorted(lineas, key=lambda l: (round(l["bbox"][1] / 2), l["bbox"][0]))
    der_blk = {}
    for l in lineas:
        if l.get("blk") is not None:
            der_blk[l["blk"]] = max(der_blk.get(l["blk"], 0), l["bbox"][2])
    res = []
    cur = None
    for l in lineas:
        t = l["text"]
        primero = t[:1]
        es_bullet = primero in BULLETS and (len(t) == 1 or t[1:2] in " \t" or primero in CHECK or ord(primero) >= 0xE000)
        if cur is not None and not es_bullet:
            gap = l["bbox"][1] - cur["bbox"][3]
            mismo = abs(l["size"] - cur["size"]) < 1.5
            # continuación si el hueco es pequeño, mismo tamaño y no hay salto grande de x
            izq = abs(l["bbox"][0] - cur["bbox"][0]) < 4 or (cur.get("bullet") and 0 <= l["bbox"][0] - cur["bbox"][0] < 26)
            pares = [o["bbox"][2] for o in lineas if abs(o["bbox"][0] - cur["bbox"][0]) < 4 and abs(o["bbox"][1] - cur["bbox"][1]) < 90 and abs(o["size"] - cur["size"]) < 1.5]
            d_ = max(pares) if len(pares) >= 2 else der
            lleno = d_ and cur.get("x1", 0) >= d_ - 0.07 * max(1, d_ - cur["bbox"][0])
            suelto = izq and lleno and gap < 2.6 * l["size"] and l["bbox"][0] - cur["bbox"][0] > -4
            neg_cur = all(estilo_span(x)[0] for x in cur["spans"] if x["text"].strip())
            neg_l = all(estilo_span(x)[0] for x in l["spans"] if x["text"].strip())
            titulo_suelto = neg_cur and not neg_l and len(cur["text"]) < 110 and not cur.get("bullet")
            if (gap < 0.55 * l["size"] or suelto) and mismo and not cur.get("solo") and not titulo_suelto:
                cur["spans"] += [dict(s, text=" " + s["text"]) if i == 0 else s for i, s in enumerate(l["spans"])]
                cur["bbox"] = (min(cur["bbox"][0], l["bbox"][0]), cur["bbox"][1], max(cur["bbox"][2], l["bbox"][2]), l["bbox"][3])
                cur["text"] += " " + t
                cur["x1"] = l["bbox"][2]
                continue
        cur = {"bbox": tuple(l["bbox"]), "spans": [dict(s) for s in l["spans"]], "text": t, "size": l["size"], "bullet": es_bullet, "blk": l.get("blk"), "x1": l["bbox"][2]}
        if es_bullet:
            # quita el símbolo
            sp = cur["spans"]
            if primero in BULLETS and sp[0]["text"].strip()[:1] == primero:
                sp[0]["text"] = sp[0]["text"].lstrip()[1:].lstrip()
                if not sp[0]["text"]:
                    sp.pop(0)
            cur["check"] = primero in CHECK
            cur["text"] = t[1:].strip() if primero in BULLETS else t
        res.append(cur)
    return res


def clasificar(p, tam_cuerpo, sobre_caja):
    spans = [s for s in p["spans"] if s["text"].strip()]
    if not spans:
        return "vacio"
    estilos = [estilo_span(s) for s in spans]
    todo_neg = all(e[0] for e in estilos)
    todo_ac = all(e[2] for e in estilos)
    n = len(p["text"])
    if p.get("bullet"):
        return "li"
    if p["text"].startswith("FASE ") and p["text"].isupper() and p["size"] < tam_cuerpo:
        return "lab"
    if p["size"] >= 1.7 * tam_cuerpo and n < 120 and not re.fullmatch(r"[\d\s%+.,]+", p["text"].strip()):
        return "h2"
    if sobre_caja and n < 160 and (todo_neg or p["size"] >= tam_cuerpo + 2):
        return "h2"
    if todo_neg and (todo_ac or p["size"] >= tam_cuerpo + 2.5) and n < 140:
        return "h2" if p["size"] >= tam_cuerpo + 6 else "h3"
    if todo_neg and n < 70 and p["size"] >= tam_cuerpo + 0.8:
        return "h3"
    if n < 90 and p["size"] >= tam_cuerpo + 2.5:
        return "h3"
    if todo_ac and not todo_neg and n < 60 and not any(s.get("href") for s in spans):
        return "lab"
    return "p"


def render_clip(doc, page, rect, destino, nombre, ancho_max=1100):
    rect = rect & page.rect
    if rect.is_empty or rect.width < 20 or rect.height < 20:
        return None
    z = min(3.0, ancho_max / rect.width)
    z = max(z, 1.2)
    pm = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=rect, alpha=False)
    im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    ruta = os.path.join(destino, nombre)
    im.save(ruta, "JPEG", quality=84, optimize=True, progressive=True)
    return (nombre, im.width, im.height)


_LOGO = None
def _ahash(im):
    g = im.convert("L").resize((16, 16))
    px = list(g.getdata()); m = sum(px) / len(px)
    return [1 if v > m else 0 for v in px]

def es_logo(im):
    global _LOGO
    if _LOGO is None:
        lg = Image.open(DESTINO + "assets/logo-evorehab.png").convert("RGBA")
        f = Image.new("RGB", lg.size, "white"); f.paste(lg, mask=lg.split()[3])
        _LOGO = _ahash(f)
    h = _ahash(im)
    return sum(a != b for a, b in zip(h, _LOGO)) < 40

def render_xref(doc, xref, destino, nombre, ancho_max=1100):
    if not xref:
        return None
    try:
        pm = pymupdf.Pixmap(doc, xref)
        info = doc.extract_image(xref)
        sm = info.get("smask", 0)
        if sm:
            m = pymupdf.Pixmap(doc, sm)
            pm = pymupdf.Pixmap(pm, m)
        if pm.colorspace is None or pm.colorspace.n != 3:
            pm = pymupdf.Pixmap(pymupdf.csRGB, pm)
        mode = "RGBA" if pm.alpha else "RGB"
        im = Image.frombytes(mode, (pm.width, pm.height), pm.samples)
        if mode == "RGBA":
            fondo = Image.new("RGB", im.size, "white"); fondo.paste(im, mask=im.split()[3]); im = fondo
        if es_logo(im):
            return "LOGO"
        if im.width > ancho_max:
            im = im.resize((ancho_max, round(im.height * ancho_max / im.width)), Image.LANCZOS)
        im.save(os.path.join(destino, nombre), "JPEG", quality=85, optimize=True, progressive=True)
        return (nombre, im.width, im.height)
    except Exception as e:
        return None


def procesar(doc, destino, nombre_base, num=0):
    os.makedirs(destino, exist_ok=True)
    elementos = []  # (pagina, y, x, tipo, datos)
    titulo = []
    lead = []
    imgcount = 0
    tamanos = []
    for pi, page in enumerate(doc):
        if pi == 0 and num not in SIN_PORTADA:
            continue
        lin, _ = segmentar(page, False)
        for l in lin:
            if l["bbox"][1] > 90:
                tamanos.append((round(l["size"]), len(l["text"])))
    from collections import Counter
    c = Counter()
    for t, n in tamanos:
        c[t] += n
    tam_cuerpo = c.most_common(1)[0][0] if c else 12

    for pi, page in enumerate(doc):
        pw, ph = page.rect.width, page.rect.height
        lin, links = segmentar(page, pi == 0)
        infos = page.get_image_info(xrefs=True)
        # --- imágenes útiles
        imgs = []
        MAPA = {}
        for im in infos:
            r = pymupdf.Rect(im["bbox"])
            MAPA[tuple(round(v) for v in im["bbox"])] = im.get("xref", 0)
            if r.get_area() > 0.6 * pw * ph:
                continue                      # fondos
            if pi > 0 and r.y0 <= 3 and r.width >= 520 and r.y1 <= 320:
                continue                      # banda de cabecera
            if pi > 0 and r.y1 <= 90:
                continue                      # logo de cabecera
            if r.width < 45 or r.height < 45:
                continue
            imgs.append(r)
        # quita duplicadas (mismo rect)
        unicas = []
        for r in imgs:
            if not any(abs(r.x0 - u.x0) < 4 and abs(r.y0 - u.y0) < 4 and abs(r.x1 - u.x1) < 4 and abs(r.y1 - u.y1) < 4 for u in unicas):
                unicas.append(r)
        # imágenes que contienen texto = cajas de título; las demás van a la página
        cajas = []
        reales = []
        for r in unicas:
            dentro = [l for l in lin if pymupdf.Rect(l["bbox"]).intersects(r) and (pymupdf.Rect(l["bbox"]) & r).get_area() > 0.9 * pymupdf.Rect(l["bbox"]).get_area()]
            if r.width >= 480 and r.width / r.height >= 4.4 and r.y0 > 3:
                reales.append(r)          # título en cápsula (imagen): texto de debajo no es suyo
            elif dentro and r.height < 260:
                cajas.append(r)
            elif dentro and r.height >= 260 and pi == 0:
                cajas.append(r)
            else:
                reales.append(r)
        # imagen grande con otras encima = montaje: se renderiza la zona y se descartan las de encima
        CLIPS = set()
        CLIPR = []
        for r in list(reales):
            dentro_ = [o for o in reales if o is not r and o.get_area() < r.get_area() and (o & r).get_area() > 0.9 * o.get_area()]
            if dentro_:
                CLIPS.add(tuple(round(v) for v in (r.x0, r.y0, r.x1, r.y1)))
                CLIPR.append(r)
                reales = [o for o in reales if not any(o is d_ for d_ in dentro_)]
        # imágenes pequeñas pegadas (p.ej. fotos en montaje de portada) en portada se ignoran
        portada = (pi == 0 and num not in SIN_PORTADA)
        if portada:
            reales = []
        # --- cabecera: fuera (solo si la página lleva banda de cabecera; si no, solo la regex CABECERA)
        banda = any(pymupdf.Rect(im_["bbox"]).y0 <= 3 and pymupdf.Rect(im_["bbox"]).width >= 520 and pymupdf.Rect(im_["bbox"]).y1 <= 320 for im_ in infos)
        util = []
        for l in lin:
            y0 = l["bbox"][1]
            if pi > 0 and y0 < 85 and banda:
                continue
            mk = re.match(r"FA\s*S\s*E\s*(\d)", l["text"]) if num == 11 else None
            if mk:
                l = dict(l, text=KICKERS_11[mk.group(1)], spans=[dict(l["spans"][0], text=KICKERS_11[mk.group(1)])])
            if re.fullmatch(r"\d", l["text"].strip()) and l["size"] > 60:
                continue                      # número decorativo gigante
            if CABECERA.match(l["text"].strip()):
                continue
            if y0 > ph * 0.88 and re.fullmatch(r"\d{1,2}", l["text"].strip()):
                continue
            util.append(l)
        if CLIPR:
            util = [l for l in util if not any(cr.contains(pymupdf.Point((l['bbox'][0] + l['bbox'][2]) / 2, (l['bbox'][1] + l['bbox'][3]) / 2)) for cr in CLIPR)]
        if num in SIN_PORTADA and pi == 0:
            titulo = list(SIN_PORTADA[num][:1])
        if portada:
            if not util:
                continue
            util = [l for l in util if not AUTOR.search(l["text"])]
            mx = max(l["size"] for l in util)
            tit = [l for l in util if l["size"] >= 0.9 * mx or (l["size"] >= 0.7 * mx and l["size"] >= 35)]
            resto = [l for l in util if l not in tit and l["size"] >= 16]
            tit.sort(key=lambda l: l["bbox"][1])
            titulo = [l["text"] for l in tit]
            resto.sort(key=lambda l: l["bbox"][1])
            lead = []
            prev = None
            for l in resto:
                if prev is not None and l["bbox"][1] - prev["bbox"][3] < 0.9 * l["size"]:
                    lead[-1] += " " + l["text"]
                else:
                    lead.append(l["text"])
                prev = l
            continue
        for (ry0, ry1) in REGIONES.get(num, {}).get(pi, []):
            util = [l for l in util if not (ry0 <= (l["bbox"][1] + l["bbox"][3]) / 2 <= ry1)]
            imgcount += 1
            rr = pymupdf.Rect(40, ry0, pw - 40, ry1)
            inf = render_clip(doc, page, rr, destino, f"img-{imgcount:02d}.jpg")
            if inf:
                elementos.append((pi, ry0, 0, "img", [inf + (100,)]))
            reales = [r_ for r_ in reales if not (ry0 - 5 <= r_.y0 and r_.y1 <= ry1 + 5)]
        if REGIONES.get(num, {}).get(pi) and not util and not reales:
            continue
        # --- páginas sin texto: renderizar cuerpo completo
        chars = sum(len(l["text"]) for l in util)
        dib = len(page.get_drawings())
        if chars < 60 and not reales:
            r = pymupdf.Rect(20, 100, pw - 20, ph - 20)
            # recorta el blanco
            pm = page.get_pixmap(clip=r, dpi=50)
            im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
            bb = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
            if bb:
                f = r.width / pm.width
                r = pymupdf.Rect(r.x0 + bb[0] * f - 6, r.y0 + bb[1] * f - 6, r.x0 + bb[2] * f + 6, r.y0 + bb[3] * f + 6)
                imgcount += 1
                inf = render_clip(doc, page, r, destino, f"img-{imgcount:02d}.jpg")
                if inf:
                    elementos.append((pi, r.y0, 0, "img", [inf + (100,)]))
            continue
        # --- texto
        ps = parrafos(util, ph)
        for p in ps:
            pr = pymupdf.Rect(p["bbox"])
            sobre = any((pr & c_).get_area() > 0.6 * pr.get_area() for c_ in cajas)
            k = clasificar(p, tam_cuerpo, sobre)
            if k == "vacio":
                continue
            elementos.append((pi, p["bbox"][1], p["bbox"][0], k, p))
        # --- imágenes (agrupa filas)
        reales.sort(key=lambda r: (r.y0, r.x0))
        filas = []
        for r in reales:
            for f_ in filas:
                if r.y0 < f_[-1].y1 - 5 and r.y1 > f_[-1].y0 + 5:
                    f_.append(r); break
            else:
                filas.append([r])
        for f_ in filas:
            infs = []
            for r in sorted(f_, key=lambda r: r.x0):
                imgcount += 1
                inf = None if tuple(round(v) for v in (r.x0, r.y0, r.x1, r.y1)) in CLIPS else render_xref(doc, MAPA.get(tuple(round(v) for v in (r.x0, r.y0, r.x1, r.y1))), destino, f"img-{imgcount:02d}.jpg", 1100 if len(f_) == 1 else 700)
                if inf == "LOGO":
                    imgcount -= 1
                    continue
                inf = inf or render_clip(doc, page, r, destino, f"img-{imgcount:02d}.jpg", 1100 if len(f_) == 1 else 700)
                if inf: infs.append(tuple(inf) + (min(100, round(100 * r.width / (pw * 0.85))),))
            if infs:
                elementos.append((pi, f_[0].y0, 0, "img", infs))
    elementos.sort(key=lambda e: (e[0], e[1], e[2]))
    res = []
    pend = None
    for e in elementos:
        if e[3] in ("h2", "h3") and re.fullmatch(r"\d{1,2}", e[4]["text"].strip()):
            pend = e[4]["text"].strip()
            continue
        if pend and e[3] in ("h2", "h3", "p"):
            e[4]["spans"].insert(0, dict(e[4]["spans"][0], text=pend + ". ", href=None))
        pend = None if e[3] in ("h2", "h3", "p") else pend
        res.append(e)
    return titulo, lead, res


def miniatura_yt(i, vertical, destino, nombre):
    try:
        data = urllib.request.urlopen(f"https://img.youtube.com/vi/{i}/maxresdefault.jpg", timeout=20).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        data = urllib.request.urlopen(f"https://img.youtube.com/vi/{i}/hqdefault.jpg", timeout=20).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    if vertical:
        cw = round(h * 9 / 16); x = (w - cw) // 2
        im = im.crop((x, 0, x + cw, h))
    im.save(os.path.join(destino, nombre), "JPEG", quality=82, optimize=True, progressive=True)
    return im.size


def html_contenido(elementos, destino, num=0):
    caps = list(CAPSULAS.get(num, []))
    out = []
    ul = []
    cuenta_li = 0

    def cerrar_ul():
        nonlocal ul
        if ul:
            out.append('<ul class="lm-lista">' + "".join(ul) + "</ul>")
            ul = []

    for pi, y, x, k, dat in elementos:
        if k == "li":
            cl = ' class="chk"' if dat.get("check") else ""
            ul.append(f"<li{cl}>{html_spans(dat['spans'])}</li>")
            continue
        cerrar_ul()
        if k == "img":
            if len(dat) == 1 and caps and dat[0][1] / dat[0][2] > 4.5:
                t = caps.pop(0)
                if t.startswith("~"):
                    out.append(f'<h3 class="lm-h3c">{t[1:]}</h3>')
                elif t.startswith("!"):
                    wa_t = urllib.parse.quote(t[1:])
                    out.append(f'<p class="lm-cta"><a class="btn-wa" href="https://wa.me/34644516082?text={wa_t}" target="_blank" rel="noopener noreferrer">{WA_SVG} {t[1:]}</a></p>')
                else:
                    out.append(f'<h2 class="lm-h2d">{t}</h2>')
                continue
            if len(dat) == 1:
                n, w, h, pct = dat[0]
                est = f' style="width:{pct}%;margin-left:auto;margin-right:auto"' if pct < 90 else ""
                out.append(f'<figure class="lm-fig"{est}><img loading="lazy" decoding="async" src="{n}" width="{w}" height="{h}" alt="" /></figure>')
            else:
                out.append('<div class="lm-figs">' + "".join(f'<img loading="lazy" decoding="async" src="{n}" width="{w}" height="{h}" alt="" />' for n, w, h, _p in dat) + "</div>")
            continue
        sp = [s for s in dat["spans"] if s["text"].strip()]
        hrefs = {s["href"] for s in sp}
        if len(hrefs) == 1 and None not in hrefs and len(dat["text"]) < 40 and yt_id(next(iter(hrefs))):
            u = next(iter(hrefs)); i = yt_id(u); vert = "shorts" in u
            nom = f"yt-{i}.jpg"
            try:
                w, h = miniatura_yt(i, vert, destino, nom)
            except Exception as e:
                out.append(f'<p><a href="{html.escape(u)}" target="_blank" rel="noopener noreferrer">Ver vídeo</a></p>')
                continue
            cls = "lm-vid" + ("" if vert else " h")
            out.append(f'<div class="lm-vidwrap{"" if vert else " h"}"><div class="{cls}"><a class="lm-yt" href="{html.escape(u)}" rel="noopener noreferrer" data-yt-embed="{i}" data-titulo="Vídeo"><img loading="lazy" decoding="async" width="{w}" height="{h}" src="{nom}" alt="Vídeo" /><span class="play"><span class="round">▶</span></span></a></div></div>')
            continue
        if k == "h2":
            out.append(f"<h2 class=\"lm-h2d\">{html_spans(dat['spans'])}</h2>")
        elif k == "h3":
            out.append(f"<h3 class=\"lm-h3d\">{html_spans(dat['spans'])}</h3>")
        elif k == "lab":
            out.append(f"<p class=\"lm-lab\">{esc(dat['text'])}</p>")
        else:
            out.append(f"<p>{html_spans(dat['spans'])}</p>")
    cerrar_ul()
    return "\n".join(out)


WA_SVG = '<svg class="wa-ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>'


def pagina(titulo, lead, cuerpo, kicker, num):
    t_plano = " ".join(titulo).strip()
    t_plano = re.sub(r"\s+", " ", t_plano)
    largo = " lm-largo" if len(t_plano) > 34 else ""
    h1 = esc(t_plano)
    if DESTACAR.get(num):
        h1 = re.sub("(" + re.escape(esc(DESTACAR[num])) + ")", lambda m: '<span class="cy">' + m.group(1) + "</span>", h1, count=1, flags=re.I)
    leadh = "".join(f'<p class="lm-sub">{esc(x)}</p>' for x in lead[:3])
    wa = urllib.parse.quote(f"Hola Edu! Acabo de ver «{t_plano}» y quiero comentarte mi caso")
    meta = html.escape(t_plano[:150])
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex" />
  <title>{esc(t_plano)} | EVOREHAB</title>
  <meta name="description" content="{meta}" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../landing.css?v=6" />
  <link rel="stylesheet" href="../lm.css?v=6" />
  <link rel="stylesheet" href="../cookies.css?v=1" />
</head>
<body>

<header>
  <div class="wrap">
    <span class="logo"><img src="../assets/logo-evorehab.png" alt="EVOREHAB" /></span>
  </div>
</header>

<section class="lm-hero">
  <div class="wrap">
    <span class="kicker">{esc(kicker)}</span>
    <h1 class="{largo.strip()}" style="margin-top:18px">{h1}</h1>
    {leadh}
    <div class="lm-yo">
      <div class="lm-yo-fotos" aria-hidden="true">
        <span class="lm-ring r1"><img src="../assets/yo-salto.jpg" alt="" /></span>
        <span class="lm-ring r2"><img src="../assets/yo-sentadilla.jpg" alt="" /></span>
        <span class="lm-ring r3"><img src="../assets/yo-graduacion.jpg" alt="" /></span>
      </div>
      <div class="lm-yo-txt">
        <b>Eduardo Estévez</b>
        <span class="lm-yo-user">@edu.rehab</span>
        <p>Especialista en readaptación de lesiones de rodilla</p>
        <ul>
          <li>Ciencias de la A.F. y el deporte · UAH</li>
          <li>Experto universitario PT · Uni. LaSalle</li>
          <li>Múltiples formaciones de referentes del sector</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="lm-sec">
  <div class="wrap">
    <div class="lm-doc">
{cuerpo}
    </div>
  </div>
</section>

<section class="lm-sec lm-fin">
  <div class="wrap">
    {"" if num in SIN_CIERRE else f'''<div class="lm-cierre">
      <p><strong>¿Quieres que lo veamos aplicado a tu caso?</strong> Cada rodilla y cada proceso es distinto, y muchas veces pequeños ajustes marcan una gran diferencia.</p>
      <a class="btn-wa" href="https://wa.me/34644516082?text={wa}" target="_blank" rel="noopener noreferrer">{WA_SVG} Escríbeme sin compromiso</a>
    </div>'''}
  </div>
</section>

<footer>© EVOREHAB · @edu.rehab<a class="ck-enlace" href="../cookies/" data-cookies>Cookies</a></footer>

<script src="../cookies.js?v=2"></script>
</body>
</html>
"""


def main(sel=None):
    for num, slug, pdf, kicker in LMS:
        if sel and num not in sel:
            continue
        carpeta = f"lm{num}-{slug}"
        destino = os.path.join(DESTINO, carpeta)
        if os.path.isdir(destino):
            for f in os.listdir(destino):
                if f.startswith("img-") or f.startswith("yt-"):
                    os.remove(os.path.join(destino, f))
        doc = pymupdf.open(ORIGEN + pdf)
        titulo, lead, el = procesar(doc, destino, slug, num)
        cuerpo = html_contenido(el, destino, num)
        with open(os.path.join(destino, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(pagina(titulo, lead, cuerpo, kicker, num))
        print(carpeta, "|", " ".join(titulo)[:60], "| elementos:", len(el))


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or None)
