# Timelapse (moonraker-timelapse)

Макросы таймлапса — в `printer.cfg` (секция `# ТАЙМЛАПС`).

## Установка на RPi

```bash
cd ~
git clone https://github.com/mainsail-crew/moonraker-timelapse.git
cd moonraker-timelapse
./install.sh
```

В `moonraker.conf` после установки появится `[timelapse]`. Камера — **chamber** (см. `doc/cameras_setup.md`).

## Orca Slicer

**Machine G-code → Layer change:**

```gcode
TIMELAPSE_TAKE_FRAME
```

## Включение

Консоль Klipper / Mainsail:

```
_SET_TIMELAPSE_SETUP ENABLE=True PARK_ENABLE=True
GET_TIMELAPSE_SETUP
```

Паркинг по умолчанию — задний угол (`PARK_POS=back_left` для Voron 500).

## Без плагина

Если moonraker-timelapse не установлен — **удалите** `TIMELAPSE_TAKE_FRAME` из слайсера и закомментируйте секцию `# ТАЙМЛАПС` в `printer.cfg`.
