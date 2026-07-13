#!/bin/bash
# Быстрая установка одной USB-камеры (Crowsnest + Moonraker) на MainsailOS / Pi.
# Запуск на Raspberry Pi: bash install-single-camera.sh
set -euo pipefail

CONFIG_DIR="${HOME}/printer_data/config"
REPO_CAMS="$(cd "$(dirname "$0")" && pwd)"

echo "=== USB cameras (video-index0 only) ==="
ls -la /dev/v4l/by-id/*-video-index0 2>/dev/null || {
    echo "ERROR: No /dev/v4l/by-id/*-video-index0 — камера не видна. Проверьте USB и lsusb."
    exit 1
}

DEVICE="$(ls /dev/v4l/by-id/*-video-index0 | head -1)"
echo "Using device: ${DEVICE}"

mkdir -p "${CONFIG_DIR}"

cp "${REPO_CAMS}/crowsnest.conf.example" "${CONFIG_DIR}/crowsnest.conf"
sed -i "s|^device:.*|device: ${DEVICE}|" "${CONFIG_DIR}/crowsnest.conf"

cp "${REPO_CAMS}/moonraker-webcams.conf.example" "${CONFIG_DIR}/moonraker-webcams.conf"

if ! grep -q 'moonraker-webcams.conf' "${CONFIG_DIR}/moonraker.conf" 2>/dev/null; then
    printf '\n[include moonraker-webcams.conf]\n' >> "${CONFIG_DIR}/moonraker.conf"
    echo "Added [include moonraker-webcams.conf] to moonraker.conf"
fi

# Убрать устаревшую nozzle webcam из moonraker.conf, если осталась
if grep -q '^\[webcam nozzle\]' "${CONFIG_DIR}/moonraker.conf" 2>/dev/null; then
    echo "WARN: В moonraker.conf есть [webcam nozzle] — удалите вручную или оставьте только include."
fi

echo "=== Restart services ==="
sudo systemctl restart crowsnest
sudo systemctl restart moonraker

sleep 2
echo "=== Crowsnest log (last 20 lines) ==="
journalctl -u crowsnest -n 20 --no-pager || true

echo "=== Stream check ==="
curl -sI "http://127.0.0.1/webcam/?action=stream" | head -5 || true

echo "=== Moonraker webcams ==="
curl -s "http://127.0.0.1:7125/server/webcams/list" | python3 -m json.tool 2>/dev/null || true

echo ""
echo "Откройте в браузере: http://<IP-принтера>/webcam/?action=stream"
echo "Mainsail: Настройки → Камеры → chamber → показать на дашборде"
