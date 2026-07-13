# Камера — Voron 2.4 Gr1mSkull (1× USB, обзор корпуса)

Одна USB-камера на Raspberry Pi 4B (MainsailOS): **Crowsnest** (стрим) + **Moonraker** (регистрация в Mainsail).

Документация Crowsnest: https://docs.mainsail.xyz/crowsnest/

---

## Быстрая установка (на Pi)

```bash
cd ~/Voron2.4_Gr1mSkull/klipper_config_mks_monster8/cameras   # путь к клону репозитория
bash install-single-camera.sh
```

Скрипт подставит первый `*-video-index0` из `/dev/v4l/by-id/`, скопирует конфиги и перезапустит службы.

---

## 1. Проверить, что Pi видит камеру

```bash
lsusb
ls -la /dev/v4l/by-id/*-video-index0
v4l2-ctl --list-devices
```

**Важно:** у одной USB-камеры часто два узла (`video0` + `video1`). В Crowsnest указывайте только **`*-video-index0`**, не metadata-узел.

Типичная камера корпуса (Gr1mSkull): `1908:2311` Generic USB2.0 PC CAMERA.

Пример пути:

```
/dev/v4l/by-id/usb-Generic_USB2.0_PC_CAMERA-video-index0
```

После отключения камеры с сопла путь **может измениться** — всегда проверяйте `by-id` заново.

---

## 2. Crowsnest — одна камера

Файл на Pi: **`~/printer_data/config/crowsnest.conf`**

```bash
cp klipper_config_mks_monster8/cameras/crowsnest.conf.example ~/printer_data/config/crowsnest.conf
nano ~/printer_data/config/crowsnest.conf
```

Замените строку `device:` на ваш путь из шага 1.

| Параметр | Значение |
|----------|----------|
| Блок | `[cam chamber]` |
| Порт | `8080` |
| URL в Mainsail | `/webcam/?action=stream` |

**Удалите** второй блок `[cam nozzle]` и порт `8081`, если он остался от старой двухкамерной схемы — иначе Crowsnest может не стартовать или Mainsail будет ждать `/webcam2/`.

Перезапуск:

```bash
sudo systemctl restart crowsnest
journalctl -u crowsnest -n 40 --no-pager
```

В логе не должно быть `Cannot open device` / `No such file`.

Проверка в браузере (после входа в Mainsail):

```
http://<IP-принтера>/webcam/?action=stream
```

На Pi:

```bash
curl -I http://127.0.0.1/webcam/?action=stream
```

Ожидается `HTTP/1.1 200` или `Content-Type: multipart/x-mixed-replace`.

---

## 3. Moonraker — одна webcam

Файл: **`~/printer_data/config/moonraker-webcams.conf`**

```bash
cp klipper_config_mks_monster8/cameras/moonraker-webcams.conf.example ~/printer_data/config/moonraker-webcams.conf
```

В **`~/printer_data/config/moonraker.conf`**:

```ini
[include moonraker-webcams.conf]
```

**Удалите** из `moonraker.conf` (если есть):

- `[webcam nozzle]` с `/webcam2/`
- старую одиночную секцию `[webcam]` без имени
- дублирующие `stream_url` на несуществующий поток

```bash
sudo systemctl restart moonraker
curl -s http://127.0.0.1:7125/server/webcams/list | python3 -m json.tool
```

Должна быть одна запись **`chamber`**, `enabled: true`.

---

## 4. Mainsail

1. **Ctrl+Shift+R** — жёсткое обновление страницы
2. **Настройки → Камеры** — только **chamber**, stream `/webcam/?action=stream`
3. Удалите или отключите камеру **nozzle** (если осталась в UI)
4. На дашборде: иконка камеры → выбрать **chamber**

Ручное добавление, если список пуст:

| Поле | Значение |
|------|----------|
| Имя | chamber |
| Stream URL | `/webcam/?action=stream` |
| Snapshot URL | `/webcam/?action=snapshot` |
| Service | crowsnest |

---

## 5. Типичные проблемы

| Симптом | Решение |
|---------|---------|
| Чёрный экран | Неверный `device:` — только `by-id/*-video-index0`; попробуйте `mode: ustreamer` вместо `camera-streamer` |
| 404 на `/webcam/` | `systemctl status crowsnest` — служба не запущена; смотрите `journalctl -u crowsnest` |
| Работает `/webcam2/`, не `/webcam/` | В `crowsnest.conf` осталась только nozzle на 8081 — оставьте один `[cam chamber]` на 8080 |
| Mainsail пусто, URL в браузере OK | Нет `[webcam chamber]` в Moonraker — шаг 3 |
| `InterpolationSyntaxError: '%LOGPATH%'` | Python 3.13: в `crowsnest.conf` уже `log_path: %%LOGPATH%%` |
| Высокая нагрузка на Pi | `resolution: 640x480`, `max_fps: 10` |
| Камера пропала после перестановки USB | Снова `ls /dev/v4l/by-id/` и обновить `device:` |

### Поворот

В `crowsnest.conf`:

```ini
#v4l2ctl: rotate=180
```

Или в Mainsail → настройки webcam → rotation.

---

## 6. Таймлапс

Moonraker-timelapse использует камеру **chamber** (порт 8080). См. `doc/timelapse_setup.md`.

---

## 7. Чеклист

- [ ] `ls /dev/v4l/by-id/*-video-index0` — один путь
- [ ] `crowsnest.conf` — один `[cam chamber]`, порт 8080, верный `device:`
- [ ] Нет `[cam nozzle]` / порта 8081
- [ ] `systemctl restart crowsnest` — без ошибок
- [ ] Браузер: `/webcam/?action=stream` показывает видео
- [ ] `moonraker-webcams.conf` — только `[webcam chamber]`
- [ ] Mainsail — chamber на дашборде

Шаблоны: `klipper_config_mks_monster8/cameras/`
