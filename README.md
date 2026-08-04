# Mini térmica bluetooth YHK-59A8

Impresora térmica de 58 mm (384 px de cabezal), MAC `F6:2E:54:27:59:A8`.

Base: [abhigkar/YHK-Cat-Thermal-Printer](https://github.com/abhigkar/YHK-Cat-Thermal-Printer),
con la MAC ya puesta y el bloque final de `cat-printer.py` cambiado para tomar argumentos.

## Lo importante

**Habla por Bluetooth Classic, RFCOMM canal 2.** El canal 1 devuelve
`[Errno 111] Connection refused`.

Por BLE la impresora **acepta los bytes y los ignora en silencio**: alimenta papel y sale en
blanco. Por eso no sirven ni Web Bluetooth ni proyectos como `TiMini-Print`, que solo intenta el
canal 1 y después cae a BLE.

Dos rarezas del firmware que ningún filtro ESC/POS genérico manda:

- `1D 49 F0 19` antes del raster (inicio de impresión propio de este firmware)
- la imagen va **rotada 180°**, si no sale de cabeza

## Uso directo (sin CUPS)

```bash
.venv/bin/python cat-printer.py imagen.png
.venv/bin/python cat-printer.py -t "texto"
```

Sirve para probar el hardware sin CUPS de por medio cuando algo falla.

## Como impresora del sistema

```bash
sudo cups/instalar.sh
lp -d Obsedium_Termica archivo.pdf
```

Después aparece en el diálogo de impresión de Chrome y de cualquier app.

| Archivo | Qué es |
|---|---|
| `cups/yhk` | Backend CUPS: abre el socket RFCOMM y copia el trabajo |
| `cups/rastertoyhk` | Filtro CUPS: PDF → ESC/POS (rasteriza con `pdftoppm` a 203 dpi) |
| `cups/obsedium-yhk.ppd` | Rollo de 48 mm, 203 dpi, monocromo |
| `cups/instalar.sh` | Copia todo a su lugar y crea la cola `Obsedium_Termica` |

Detalles que cuestan de descubrir:

- El backend de **bluez-cups no sirve**: ignora la `DEVICE_URI` que se le pasa, y su
  descubrimiento filtra por clase de dispositivo Imaging (6) mientras esta impresora se declara
  **clase 9 (Health)**.
- El filtro corre como usuario `lp`, que **no ve los paquetes de `~/.local`**. De ahí el
  `python3-pillow` del sistema en el instalador.
- 203 dpi no es arbitrario: a esa resolución una página de 48 mm da 384 px exactos, el ancho
  nativo del cabezal.
- El filtro recorta el blanco sobrante del final. Sin eso, cada etiqueta escupe la hoja completa
  del PPD y se come el rollo.

Si la cola queda en `processing` sin imprimir, mirar `/var/log/cups/error_log`; lo primero a
probar es `sudo chmod 0700 /usr/lib/cups/backend/yhk` (lo pasa a correr como root).

## Obsedium OS

El dashboard (`!Dashboard`) tiene un selector **A4 / Térmica** en la barra de selección de
etiquetas: en térmica cambia `@page` a `48mm auto` y la grilla a una columna. Hay que elegirlo
antes de imprimir, porque el CSS de `@page` se resuelve antes de que se abra el diálogo del
navegador.
