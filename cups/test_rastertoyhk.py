#!/usr/bin/python3
"""Check minimo del filtro: la hoja llega al cabezal a escala fisica y
centrada, sin deformarse. Correr: python3 cups/test_rastertoyhk.py"""
import importlib.machinery
import importlib.util
import os

import numpy as np
from PIL import Image, ImageDraw

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rastertoyhk")
spec = importlib.util.spec_from_loader(
    "rastertoyhk", importlib.machinery.SourceFileLoader("rastertoyhk", ruta))
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

PX_POR_MM = f.DPI / 25.4          # como rasteriza pdftoppm
CABEZAL_MM = f.ANCHO / 203 * 25.4  # 48 mm


def hoja(ancho_mm, x0_mm, ancho_caja_mm):
    """Una hoja con una barra negra maciza, en pixeles de pdftoppm.

    Maciza y no de contorno: una linea de 1 px al reducirse a la mitad queda
    gris al 50% y cae justo sobre el umbral, lo que da falsos negativos.
    """
    im = Image.new("L", (round(ancho_mm * PX_POR_MM), 400), 255)
    ImageDraw.Draw(im).rectangle(
        [round(x0_mm * PX_POR_MM), 50,
         round((x0_mm + ancho_caja_mm) * PX_POR_MM) - 1, 300], fill=0)
    return im


def caja_mm(im):
    """Ancho y borde izquierdo de la tinta, en mm sobre el cabezal."""
    cols = np.where((np.array(im) < 128).sum(axis=0) > 0)[0]
    return (cols.max() - cols.min() + 1) / 203 * 25.4, cols.min() / 203 * 25.4


# Hoja de 48 mm (el dashboard): entra 1:1, sin recorte.
salida = f.a_384(f.recortar_blanco(hoja(48, 0, 48)))
assert salida.width == f.ANCHO, salida.width
ancho, izq = caja_mm(salida)
assert abs(ancho - 48) < 0.5, ancho
assert izq < 0.5, izq

# Hoja de 56 mm (MiniThermal): se pierden los 4 mm por lado que el cabezal no
# alcanza, y los 48 mm utiles quedan intactos y a escala.
salida = f.a_384(f.recortar_blanco(hoja(56, 4, 48)))
assert salida.width == f.ANCHO, salida.width
ancho, izq = caja_mm(salida)
assert abs(ancho - 48) < 0.5, ancho
assert izq < 0.5, izq

# Lo que se rompia antes: un texto corto NO se agranda hasta el ancho del
# cabezal, conserva su tamano real.
salida = f.a_384(f.recortar_blanco(hoja(56, 4, 12)))
ancho, _ = caja_mm(salida)
assert abs(ancho - 12) < 0.5, "una caja de 12 mm salio de %.1f mm" % ancho

assert f.recortar_blanco(Image.new("L", (768, 400), 255)) is None  # hoja vacia

print("OK: escala fisica conservada y centrada en los %.0f mm del cabezal"
      % CABEZAL_MM)
