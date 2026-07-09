# Kalico + Cartographer — MKS Monster8 V2.0

> Этот принтер использует **Kalico** (форк Klipper), не mainline Klipper.
> Документация: https://docs.kalico.gg

## 1. Установка Kalico (KIAUH или вручную)

```bash
cd ~
git clone https://github.com/KalicoCrew/kalico.git
cd kalico
# Следуйте https://docs.kalico.gg/Installation.html
# KIAUH: выберите Kalico вместо Klipper
```

Прошивки MCU собирайте из `~/kalico`, не из `~/klipper`.

## 2. Плагин Cartographer 3D (новый cartographer3d-plugin)

Требуется Kalico **или** Klipper ≥ 0.13. Поддержка Kalico встроена в плагин.

```bash
curl -s -L https://raw.githubusercontent.com/Cartographer3D/cartographer3d-plugin/refs/heads/main/scripts/install.sh \
  | bash -s -- --klipper ~/kalico --klippy-env ~/klippy-env
```

Прошивка пробы: https://docs.cartographer3d.com/cartographer-probe/firmware

```bash
cd ~
git clone https://github.com/Cartographer3D/cartographer_firmware.git
```

### Moonraker (`moonraker.conf`)

```ini
[update_manager cartographer_plugin]
type: python
channel: stable
virtualenv: ~/klippy-env
project_name: cartographer3d-plugin
is_system_service: False
managed_services: klipper
info_tags: desc=Cartographer Plugin

[update_manager cartographer_firmware]
type: git_repo
path: ~/cartographer_firmware
is_system_service: False
origin: https://github.com/Cartographer3D/cartographer_firmware.git
primary_branch: main
```

> Удалите старые секции `cartographer-klipper` / `cartographer-probe`, если были.

## 3. Чего НЕ должно быть в конфиге

- Секция `[probe]` с `pin` — Cartographer даёт `probe:z_virtual_endstop`
- Секция `[scanner]` — устаревший плагин (удалите из SAVE_CONFIG внизу `printer.cfg`)
- `PROBE_CALIBRATE` / `CARTOGRAPHER_TOUCH` — используйте `CARTOGRAPHER_TOUCH_HOME`
- `restart_method` в `[mcu cartographer]` при подключении по CAN

### Ошибка `Unknown pin chip name 'probe'`

1. Установите **новый** плагин (не `cartographer-klipper` / `scanner`):

```bash
curl -s -L https://raw.githubusercontent.com/Cartographer3D/cartographer3d-plugin/refs/heads/main/scripts/install.sh \
  | bash -s -- --klipper ~/kalico --klippy-env ~/klippy-env
```

2. Проверьте установку:

```bash
ls -la ~/kalico/klippy/extras/cartographer.py
~/klippy-env/bin/python -c "import cartographer; print(cartographer.__version__)"
```

3. В `printer.cfg` секции Cartographer должны быть **выше** `[stepper_z]` — в едином файле они идут сразу после `[mcu]`.

4. Удалите из SAVE_CONFIG устаревшие `[scanner]` и дубли `[stepper_z]`.

## 4. Калибровка Cartographer

1. `FIRMWARE_RESTART`
2. `G28` или `G28 X Y` — портал сначала поднимается на 15 мм, затем homing XY
3. `QUAD_GANTRY_LEVEL` → `G28 Z`
4. `CARTOGRAPHER_SCAN_CALIBRATE` → `SAVE_CONFIG`
5. `CARTOGRAPHER_TOUCH_CALIBRATE` → `SAVE_CONFIG`
6. `SHAPER_CALIBRATE` → `SAVE_CONFIG`

## 5. Особенности Kalico

- `[respond]`, `[exclude_object]`, `[force_move]` включены по умолчанию — не дублируйте в `printer.cfg`
- `SAVE_CONFIG` дописывает калибровку в конец `printer.cfg` (см. docs.kalico.gg)
- `RELOAD_GCODE_MACROS` — перезагрузка макросов без `FIRMWARE_RESTART`

## 6. CAN

См. `doc/can0_setup.md` — все пути `~/kalico`.
