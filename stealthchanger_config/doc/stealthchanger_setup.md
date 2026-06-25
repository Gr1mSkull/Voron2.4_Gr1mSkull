# StealthChanger — установка (второй принтер)

500×500×480 | Manta M8P v2.0 + CB2 (образ BTT CB2 V3.0.2 — Debian 12) | 6× EBB SB2209 CAN (RP2040) | Rapido (PT1000) | Nudge

## 1. CAN-шина (7 узлов: M8P + 6 голов) @ 1000000

`/etc/network/interfaces.d/can0`:

```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 1024
```

```bash
sudo ifup can0
```

> 7 узлов на одной шине — держите проводку короткой, витая пара, терминаторы
> 120 Ω **только на двух концах** физической шины.

Прошивка: M8P — USB-to-CAN bridge (как на 1-м принтере). Каждая голова
SB2209 RP2040 — Katapult+Klipper, CAN (gpio4/gpio5) @ 1000000.

UUID всех узлов:
```bash
sudo systemctl stop klipper
python3 ~/katapult/scripts/flash_can.py -q
sudo systemctl start klipper
```
Впишите в `mcu.cfg` (M8P) и `toolchanger/tools/T0..T5.cfg` (EBBT0..EBBT5).

## 2. klipper-toolchanger-easy

```bash
cd ~
git clone https://github.com/jwellman80/klipper-toolchanger-easy.git
cd ~/klipper-toolchanger-easy
./install.sh
```

Скрипт создаёт в `~/printer_data/config/`:
- `toolchanger/readonly-configs/` (симлинки, **НЕ редактировать**)
- `toolchanger/toolchanger-config.cfg` (пользовательский — у нас уже готов)
- `toolchanger/tools/` (примеры — заменить нашими T0..T5)

Скопируйте содержимое `stealthchanger_config/` в `~/printer_data/config/`,
**сохранив** созданный install.sh каталог `toolchanger/readonly-configs/`.

`printer.cfg` уже содержит:
```ini
[include toolchanger/readonly-configs/toolchanger-include.cfg]
```
Этот include сам подключает homing/tool_detection/toolchanger/macros/
calibrate-offsets/crash-detection, затем `tools/T*.cfg` и
`toolchanger-config.cfg` (последним — для оверрайдов).

moonraker.conf (автообновление):
```ini
[update_manager klipper-toolchanger-easy]
type: git_repo
channel: dev
path: ~/klipper-toolchanger-easy
origin: https://github.com/jwellman80/klipper-toolchanger-easy.git
managed_services: klipper
primary_branch: main
```

## 3. Что обязательно настроить

| Что | Где |
|-----|-----|
| UUID M8P | `mcu.cfg` |
| UUID голов T0..T5 | `toolchanger/tools/Tx.cfg` |
| Координаты доков `params_park_x/y/z` | каждый `Tx.cfg` |
| `homing_override_config` sensorless_x/y | `toolchanger/toolchanger-config.cfg` |
| Пин и позиция Nudge | `toolchanger-config.cfg` (`tools_calibrate`, `_CALIBRATION_SWITCH`) |
| PT1000 pullup (если нужен) | `Tx.cfg` (`pullup_resistor`) |
| Термистор стола | `heater/heater_bed.cfg` |
| QGL углы/точки 500 | `homing/quad_gantry_level.cfg` |

## 4. Порядок калибровки

1. `FIRMWARE_RESTART` — все 7 MCU online (голова должна быть на шаттле!).
2. Проверить направления моторов, `QUERY_ENDSTOPS`.
3. Откалибровать координаты доков каждой головы (StealthChanger Wiki → Calibration).
4. Проверить смену: `T0`, `T1` … `T5`, `UNSELECT_TOOL`.
5. С T0: `G28` → `QUAD_GANTRY_LEVEL` → `G28 Z`.
6. `PROBE_CALIBRATE` (OptoTap T0) → z_offset в `[tool_probe T0]`.
7. Nudge: `CALIBRATE_ALL_OFFSETS` — XY/Z смещения T1..T5 (вписать в `Tx.cfg`).
8. `PID_CALIBRATE` для extruder..extruder5 и heater_bed.
9. Input Shaper по каждой голове (раскомментируйте её `[adxl345]`, по одной!).

> ⚠ `SAVE_CONFIG` НЕ использовать для оффсетов тулов — значения вписываются
> вручную в соответствующие `Tx.cfg` (так требует klipper-toolchanger-easy).

## 5. Слайсер

Стартовый G-code:
```gcode
PRINT_START TOOL={initial_tool} TOOL_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer]
```
Завершение: `PRINT_END`.
Детали смены инструмента — DraftShift StealthChanger Wiki → Slicers.
