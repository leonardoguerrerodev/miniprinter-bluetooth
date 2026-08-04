#!/usr/bin/bash
# Instala la mini termica YHK como impresora del sistema (CUPS).
# Idempotente: se puede correr de nuevo tras editar el filtro o el backend.
set -euo pipefail

COLA=Obsedium_Termica
URI="yhk://F6-2E-54-27-59-A8/2"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -ne 0 ]]; then
  echo "Corre con sudo: sudo $0" >&2
  exit 1
fi

# El filtro corre como el usuario 'lp', que no ve el Pillow de ~/.local.
# dnf ya es idempotente, no hace falta detectar antes.
echo ">> Pillow del sistema (para el filtro)..."
dnf install -y python3-pillow

echo ">> Copiando backend, filtro y PPD..."
install -m 0755 "$AQUI/yhk"          /usr/lib/cups/backend/yhk
install -m 0755 "$AQUI/rastertoyhk"  /usr/lib/cups/filter/rastertoyhk
install -m 0644 "$AQUI/obsedium-yhk.ppd" /usr/share/cups/model/obsedium-yhk.ppd

systemctl restart cups
sleep 2

echo ">> Creando la cola $COLA..."
lpadmin -p "$COLA" -v "$URI" -P /usr/share/cups/model/obsedium-yhk.ppd -E \
        -D "Mini termica Obsedium (bluetooth)" -L "Taller"
cupsenable "$COLA"
cupsaccept "$COLA"

echo
echo "Listo. Probala con:"
echo "  lp -d $COLA archivo.pdf"
echo "Si queda en 'processing' sin imprimir, mira /var/log/cups/error_log"
echo "y probá subir el backend a root:  sudo chmod 0700 /usr/lib/cups/backend/yhk"
