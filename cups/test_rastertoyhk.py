#!/usr/bin/python3
"""Check minimo del filtro: la etiqueta sale siempre a 45 mm, la mande como
la mande el navegador. Correr: python3 cups/test_rastertoyhk.py"""
import importlib.util
import os

from PIL import Image, ImageDraw

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rastertoyhk")
spec = importlib.util.spec_from_loader("rastertoyhk",
                                       importlib.machinery.SourceFileLoader("rastertoyhk", ruta))
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def pagina(ancho_pag, x0, ancho_caja):
    """Una hoja blanca con un rectangulo negro, como el marco de la etiqueta."""
    im = Image.new("L", (ancho_pag, 400), 255)
    ImageDraw.Draw(im).rectangle([x0, 50, x0 + ancho_caja, 300], outline=0)
    return im


def marco(im):
    import numpy as np
    cols = np.where((np.array(im) < 128).sum(axis=0) > 0)[0]
    return cols.min(), cols.max()


# El ancho y la posicion que manda el navegador varian (Chrome escala por su
# cuenta cuando hay impresora seleccionada); el resultado no debe variar.
for ancho_pag, x0, ancho_caja in [(768, 50, 480), (768, 0, 720), (768, 200, 320)]:
    salida = f.a_384(f.recortar_blanco(pagina(ancho_pag, x0, ancho_caja)))
    assert salida.width == f.ANCHO, salida.width
    izq, der = marco(salida)
    assert der - izq + 1 == f.ANCHO_ETIQUETA, (ancho_pag, x0, ancho_caja, izq, der)
    assert abs(izq - (f.ANCHO - 1 - der)) <= 1, (izq, der)  # centrado

assert f.recortar_blanco(Image.new("L", (768, 400), 255)) is None  # hoja vacia

print("OK: %d px (%.1f mm) centrados en el cabezal, venga como venga la hoja"
      % (f.ANCHO_ETIQUETA, f.ANCHO_ETIQUETA / 203 * 25.4))
