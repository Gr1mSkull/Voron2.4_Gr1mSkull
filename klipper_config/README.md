# Voron 2.4 Gr1mSkull — Klipper Configuration

**Сборка:** 500×500×480 | Manta M8P v2.0 + CB2 (образ BTT CB2 V3.0.2 — Debian 12) | EBB SB2209 CAN | Clockwork 2 / Stealthburner | Bambu X1C hotend 0.4 | Voron Tap | Cartographer (опционально)

## Установка

```bash
# На CB2 — скопировать конфиг в printer_data
cp -r klipper_config/* ~/printer_data/config/
```

Отредактируйте `mcu.cfg` — подставьте CAN UUID платы M8P и EBB.

## Переключатели в printer.cfg

### XY endstops — выберите один файл:

```ini
[include endstops/endstops_xy_physical.cfg]   # ← по умолчанию
# [include endstops/endstops_xy_sensorless.cfg]
```

После смены: `FIRMWARE_RESTART`

При sensorless используйте `SGTHRS_TEST AXIS=X VALUE=80` для подбора `driver_SGTHRS`.

### Привод XY — 2 мотора или 4 (AWD):

**2WD (по умолчанию)** — ничего не включать, работают `stepper_x` / `stepper_y`.

**4WD / AWD** — раскомментируйте в `printer.cfg`:
```ini
[include drive/xy_awd.cfg]
```

Добавляет `stepper_x1` (Motor4) и `stepper_y1` (Motor8) на свободные слоты M8P.
Кинематика остаётся `corexy`, Z и QGL не меняются.

> ⚠ **Перед первым `G28`** проверьте направление доп. моторов через `FORCE_MOVE`
> (см. шапку `drive/xy_awd.cfg`). Доп. мотор должен тянуть ремень в ту же
> сторону, что и основной — иначе инвертируйте `dir_pin` (символ `!`).

Работает совместно с любым вариантом endstops (physical/sensorless): доп.
моторы концевиков не имеют, хоумятся только основные `stepper_x` / `stepper_y`.

### Cartographer — режим C:

**Включён (Tap = Z, Cartographer = mesh + IS):**
```ini
[include probes/cartographer.cfg]
[include bed_mesh/bed_mesh_cartographer.cfg]
[include input_shaper/input_shaper_cartographer.cfg]
```

**Выключен (Tap = Z + mesh, ADXL на EBB):**
```ini
# закомментируйте три строки выше и раскомментируйте:
[include bed_mesh/bed_mesh_tap.cfg]
[include input_shaper/input_shaper_ebb.cfg]
```

Обновите переменную в `macros/macros.cfg`:
```ini
variable_use_cartographer: False
```

## Порядок первичной настройки

1. CAN — `doc/can0_setup.md`
2. UUID в `mcu.cfg`
3. Cartographer serial/UUID в `probes/cartographer.cfg` (если используется)
4. `FIRMWARE_RESTART`
5. `G28 X Y` → проверка endstops
6. `G32` → QGL
7. `PROBE_CALIBRATE` → Tap Z offset
8. Cartographer: `CARTOGRAPHER_SCAN_CALIBRATE` → `SAVE_CONFIG`
9. `PID_CALIBRATE HEATER=extruder TARGET=240`
10. `PID_CALIBRATE HEATER=heater_bed TARGET=60`
11. `SHAPER_CALIBRATE` (X, затем Y)
12. `SAVE_CONFIG`

## KlipperScreen

Настраивается отдельно в `~/KlipperScreen/KlipperScreen.conf`.  
Дисплей mini12864 в конфиге **не** включён — используется KlipperScreen.

## Что откалибровать позже

| Параметр | Файл |
|----------|------|
| Токи TMC | `endstops/*.cfg`, `steppers/steppers_z.cfg`, `extruder/extruder.cfg` |
| SGTHRS (sensorless) | `endstops/endstops_xy_sensorless.cfg` |
| Направление доп. моторов AWD | `drive/xy_awd.cfg` |
| Смещение Cartographer | `probes/cartographer.cfg` |
| QGL точки 500 мм | `homing/quad_gantry_level.cfg` |
| Тип термистора стола | `heater/heater_bed.cfg` |
| Pressure advance | `extruder/extruder.cfg` |

## Структура файлов

```
klipper_config/
├── printer.cfg          → переключатели + includes
├── mcu.cfg
├── printer_base.cfg
├── endstops/
│   ├── endstops_xy_physical.cfg
│   └── endstops_xy_sensorless.cfg
├── drive/
│   └── xy_awd.cfg          # опц.: 4 мотора XY (AWD)
├── steppers/steppers_z.cfg
├── extruder/
│   ├── extruder.cfg
│   └── stealthburner.cfg
├── probes/
│   ├── tap.cfg
│   └── cartographer.cfg
├── bed_mesh/
│   ├── bed_mesh_cartographer.cfg
│   └── bed_mesh_tap.cfg
├── input_shaper/
│   ├── input_shaper_cartographer.cfg
│   └── input_shaper_ebb.cfg
├── heater/heater_bed.cfg
├── fans/fans.cfg
├── homing/
│   ├── safe_z_home.cfg
│   └── quad_gantry_level.cfg
├── macros/macros.cfg
└── doc/can0_setup.md
```

## Макросы

| Макрос | Назначение |
|--------|------------|
| `G32` | Homing + QGL |
| `PRINT_START` | Старт печати (слайсер) |
| `PRINT_END` | Завершение + парковка |
| `LIGHTS_ON/OFF/TOGGLE` | Подсветка камеры |
| `NEVERMORE_ON/OFF` | Фильтр Nevermore |
| `EXHAUST_ON/OFF` | Вытяжка |
| `STEALTH_LED` | RGB Stealthburner |
| `SGTHRS_TEST` | Подбор sensorless |

Слайсер — стартовый G-code:
```gcode
PRINT_START BED_TEMP=[bed_temperature] EXTRUDER_TEMP=[nozzle_temperature]
```

Конец:
```gcode
PRINT_END
```
