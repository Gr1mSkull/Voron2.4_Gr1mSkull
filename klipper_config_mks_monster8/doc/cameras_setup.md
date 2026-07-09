# Камеры — Voron 2.4 Gr1mSkull (RPi 4B + MainsailOS)

На Pi у вас две USB-камеры (по `lsusb`):

| USB ID | Модель | Роль (предположительно) |
|--------|--------|-------------------------|
| `1908:2311` | GEMBIRD UVC (AX2311) | обзор камеры / корпус |
| `1817:1130` | CameraWN.AHD ForwardRGB | сопло / деталь |

Точные пути устройств нужно взять на **вашем** Pi — см. шаг 1.

Стек: **Crowsnest** (стрим) + **Moonraker** (описание для Mainsail).

Документация Crowsnest: https://docs.mainsail.xyz/crowsnest/

---

## 1. Найти камеры на Pi

```bash
# Список устройств (предпочтительно by-id — не меняется при переподключении)
ls -la /dev/v4l/by-id/
ls -la /dev/v4l/by-path/

# Подробности по каждой камере
v4l2-ctl --list-devices

# Возможности (разрешение, fps)
v4l2-ctl -d /dev/video0 --list-formats-ext
```

**Важно:** у одной физической камеры часто **два** `/dev/videoN` (video + metadata).  
В Crowsnest указывайте узел с **форматом MJPG/YUYV** (обычно `video0`, `video2`…), не `video1` если это metadata.

Пример вывода `v4l2-ctl --list-devices`:

```
GEMBIRD USB2.0 Camera (usb-xhci-hcd.0-1.3):
    /dev/video0
    /dev/video1   ← часто metadata, не использовать

USB Camera (usb-xhci-hcd.0-1.4):
    /dev/video2
    /dev/video3
```

Скопируйте пути **`/dev/v4l/by-id/...-video-index0`** для каждой камеры.

---

## 2. Установить Crowsnest (если ещё нет)

На MainsailOS часто уже установлен. Проверка:

```bash
systemctl status crowsnest
ls ~/printer_data/config/crowsnest.conf
```

Если нет — через **KIAUH** → Crowsnest, или вручную: https://github.com/mainsail-crew/crowsnest

В `moonraker.conf` должна быть секция (KIAUH добавляет сам):

```ini
[update_manager crowsnest]
type: git_repo
path: ~/crowsnest
origin: https://github.com/mainsail-crew/crowsnest.git
install_script: tools/pkglist.sh
managed_services: crowsnest
is_system_service: true
```

---

## 3. Crowsnest — две камеры

Файл на Pi: **`~/printer_data/config/crowsnest.conf`**

Скопируйте шаблон из репозитория и подставьте свои `device`:

```bash
cp klipper_config_mks_monster8/cameras/crowsnest.conf.example ~/printer_data/config/crowsnest.conf
nano ~/printer_data/config/crowsnest.conf
```

**Замените** строки `device:` на пути из шага 1.

### Рекомендуемые настройки для RPi 4B

| Камера | Порт | URL в Mainsail |
|--------|------|----------------|
| Корпус (chamber) | 8080 | `/webcam/?action=stream` |
| Сопло (nozzle) | 8081 | `/webcam2/?action=stream` |

Для Pi 4 можно `mode: camera-streamer` (WebRTC, меньше нагрузка) или `ustreamer` (проще, MJPEG).

Перезапуск:

```bash
sudo systemctl restart crowsnest
journalctl -u crowsnest -n 50 --no-pager
```

В логе не должно быть ошибок `device` / `Cannot open`.

Проверка в браузере (замените IP):

```
http://<IP-принтера>/webcam/?action=stream
http://<IP-принтера>/webcam2/?action=stream
```

---

## 4. Moonraker — регистрация в Mainsail

Файл: **`~/printer_data/config/moonraker.conf`**

Добавьте (или включите через `include`):

```bash
cat ~/printer_data/config/doc/cameras/moonraker-webcams.conf.example
```

Скопируйте содержимое в конец `moonraker.conf` или:

```ini
[include moonraker-webcams.conf]
```

и положите фрагмент в `~/printer_data/config/moonraker-webcams.conf`.

Перезапуск:

```bash
sudo systemctl restart moonraker
```

В Mainsail: **Настройки → Камеры** — должны появиться **Chamber** и **Nozzle**.

---

## 5. Типичные проблемы

| Симптом | Решение |
|---------|---------|
| Чёрный экран | Неверный `/dev/video*` — используйте `by-id`, проверьте `v4l2-ctl --list-devices` |
| Камеры поменялись местами | Поменяйте `device:` в `crowsnest.conf` |
| Высокая нагрузка на Pi | `resolution: 1280x720` → `640x480`, `max_fps: 10` |
| Одна камера работает | Уникальный `port` (8080 / 8081), разные `device` |
| Нет службы crowsnest | `KIAUH` → установить Crowsnest |
| USB отваливается | Питание Pi / хаб — камеры лучше в порты Pi напрямую |

### Поворот / зеркало

В `crowsnest.conf` для камеры:

```ini
#custom_flags: --device-timeout=2
#v4l2ctl: rotate=180
```

Или в Mainsail в настройках webcam: flip / rotation.

---

## 6. Obico / таймлапсы (опционально)

Для Obico укажите stream URL основной камеры:

```
http://<IP>/webcam/?action=stream
```

Таймлапсы в Mainsail: **Timelapse** plugin (если установлен) — камера **chamber** (8080).

---

## 7. Чеклист

- [ ] `v4l2-ctl --list-devices` — два рабочих video-index0
- [ ] `crowsnest.conf` — два блока `[cam ...]`, порты 8080 и 8081
- [ ] `systemctl restart crowsnest` — без ошибок в логе
- [ ] Браузер — оба URL открываются
- [ ] `moonraker.conf` — секции `[webcam chamber]` и `[webcam nozzle]`
- [ ] Mainsail — обе камеры в интерфейсе

---

*Шаблоны: `klipper_config_mks_monster8/cameras/` в репозитории.*
