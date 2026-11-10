"""Optimiza imágenes nuevas o pesadas sin cambiar su aspecto.
Uso:  python optimizar-imagenes.py [archivos o carpetas...]     (sin argumentos: toda la carpeta actual)
- JPG/JPEG: máximo 1000 px de ancho (--ancho para cambiarlo), calidad 82, progresivo. Corrige la rotación guardada en la foto.
- PNG: sin pérdida (optimize); si pasa de 1600 px de ancho se reduce a 1600.
- Solo sustituye el archivo si queda más pequeño. Se puede ejecutar varias veces: lo ya optimizado no se toca.
- Se salta .git, node_modules, copias de seguridad, iconos y favicons (tamaños que tienen que ser exactos)."""
import os, sys
from PIL import Image, ImageOps

ANCHO_JPG = 1000
ANCHO_PNG = 1600
SALTAR = ('.git', 'node_modules', '_copias-seguridad', 'iconos', 'maquetas')
SALTAR_NOMBRE = ('favicon', 'icono', 'apple-touch')
MIN_BYTES = 60 * 1024   # por debajo de esto no merece la pena


def optimizar(f):
    ext = f.lower().rsplit('.', 1)[-1]
    if ext not in ('jpg', 'jpeg', 'png'):
        return 0
    if any(n in os.path.basename(f).lower() for n in SALTAR_NOMBRE):
        return 0
    antes = os.path.getsize(f)
    try:
        im = Image.open(f)
        im.load()
    except Exception:
        return 0
    if antes < MIN_BYTES and im.width <= (ANCHO_PNG if ext == 'png' else ANCHO_JPG):
        return 0
    tmp = f + '.tmp'
    try:
        if ext == 'png':
            if im.width > ANCHO_PNG:
                im = im.resize((ANCHO_PNG, round(im.height * ANCHO_PNG / im.width)), Image.LANCZOS)
            im.save(tmp, 'PNG', optimize=True)
        else:
            im = ImageOps.exif_transpose(im)
            if im.mode != 'RGB':
                im = im.convert('RGB')
            if im.width > ANCHO_JPG:
                im = im.resize((ANCHO_JPG, round(im.height * ANCHO_JPG / im.width)), Image.LANCZOS)
            im.save(tmp, 'JPEG', quality=82, optimize=True, progressive=True)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        return 0
    despues = os.path.getsize(tmp)
    if despues < antes * 0.97:
        os.replace(tmp, f)
        print('  %s: %d KB -> %d KB' % (f, antes // 1024, despues // 1024))
        return antes - despues
    os.remove(tmp)
    return 0


def main(args):
    global ANCHO_JPG
    if '--ancho' in args:
        i = args.index('--ancho')
        ANCHO_JPG = int(args[i + 1])
        del args[i:i + 2]
    rutas = args or ['.']
    ahorro = 0
    for r in rutas:
        if os.path.isfile(r):
            ahorro += optimizar(r)
            continue
        for raiz, dirs, files in os.walk(r):
            dirs[:] = [d for d in dirs if d not in SALTAR]
            for n in files:
                ahorro += optimizar(os.path.join(raiz, n))
    print('Ahorrado: %.1f MB' % (ahorro / 1048576))


if __name__ == '__main__':
    main(sys.argv[1:])
