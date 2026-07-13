# Voron 2.4 — Kalico Configuration (MKS Monster8 V2.0 + RPi 4B)

**Сборка:** 500×500×480 | MKS Monster8 | EBB SB2209 CAN (STM32G0) | Stealthburner | **Cartographer 3D**

**Эталон платы** (тот же производитель, MKS Monster8 V2, 500): [deflord/3def SB2040V3/500](https://github.com/deflord/3def/tree/main/Конфигурационные%20файлы/MKS%208V2/SB2040V3/500) — совпадают пины корпуса/стола; у нас EBB SB2209 вместо SB2040 и Cartographer вместо Klicky.

> **Прошивка хоста: [Kalico](https://docs.kalico.gg)** — форк Klipper.
> Плагин: [cartographer3d-plugin](https://docs.cartographer3d.com)

## Установка

```bash
cp klipper_config_mks_monster8/printer.cfg ~/printer_data/config/
# документация (опционально):
cp -r klipper_config_mks_monster8/doc ~/printer_data/config/
```

1. Установите Kalico — `doc/kalico_setup.md`
2. Установите плагин Cartographer (путь `~/kalico`)
3. Пропишите CAN UUID в начале `printer.cfg` (секции `[mcu]`, `[mcu EBBCan]`, `[mcu cartographer]`)
4. `FIRMWARE_RESTART`

Весь конфиг — **один файл** `printer.cfg`. XY — **2WD sensorless** (TMC StallGuard). Z — Cartographer 3D (scan + touch). EBB — **STM32G0** (пины `PA*` / `PD*` / `PB*`).

**Камеры (2× USB):** `doc/cameras_setup.md` + шаблоны в `cameras/`.

## Калибровка

Полный пошаговый алгоритм: **`doc/calibration.md`** (sensorless XY, Cartographer, QGL, Input Shaper, PID, слайсер, первая печать).

Кратко:

| Шаг | Команда |
|-----|---------|
| 1 | `G28 X Y` |
| 2 | **`CARTOGRAPHER_SCAN_CALIBRATE`** → `SAVE_CONFIG` (иначе G28 Z: *Scan model not loaded*) |
| 3 | `G28 Z` → `QUAD_GANTRY_LEVEL` → `G28 Z` |
| 4 | `CARTOGRAPHER_TOUCH_CALIBRATE` → `SAVE_CONFIG` |
| 5 | `SHAPER_CALIBRATE` → `SAVE_CONFIG` |
| 6 | PID сопла и стола |

## G-code слайсера

Готовые блоки для **Orca Slicer** и **Bambu Studio**: `doc/slicer_gcode.md`

```gcode
; Старт
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer] MESH_MIN_X={adaptive_bed_mesh_min[0]} MESH_MIN_Y={adaptive_bed_mesh_min[1]} MESH_MAX_X={adaptive_bed_mesh_max[0]} MESH_MAX_Y={adaptive_bed_mesh_max[1]} PROBE_COUNT_X={bed_mesh_probe_count[0]} PROBE_COUNT_Y={bed_mesh_probe_count[1]} MESH_ALGO=[bed_mesh_algo]

; Конец
PRINT_END
```

Включите **Label objects** в настройках печати (adaptive mesh).

## Структура

```
klipper_config_mks_monster8/
├── printer.cfg            ← весь конфиг (единый файл)
├── cameras/               ← шаблоны crowsnest + moonraker
└── doc/
    ├── kalico_setup.md
    ├── can0_setup.md
    ├── calibration.md
    ├── cameras_setup.md
    └── slicer_gcode.md
```

## Макросы

| Макрос | Назначение |
|--------|------------|
| `G32` | Homing + QGL (без mesh) |
| `PRINT_START` | Старт: Orca adaptive mesh + touch + purge |
| `PRINT_END` | Завершение печати |
| `PURGE_LINE` | Только продувка (тест) |
| `MESH` | Ручная сетка (`MESH ADAPTIVE=1` — по объекту) |
