# Voron 2.4 — Kalico Configuration (MKS Monster8 V2.0 + RPi 4B)

**Сборка:** 500×500×480 | MKS Monster8 | EBB SB2209 CAN | Stealthburner | **Cartographer 3D** (без Tap)

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

Весь конфиг — **один файл** `printer.cfg`. Переключатели (физические/sensorless концевики, AWD, Voron Tap) — закомментированные блоки внутри файла.

## Калибровка

| Шаг | Команда |
|-----|---------|
| 1 | `G28 X Y` |
| 2 | `G32` или `QUAD_GANTRY_LEVEL` + `G28 Z` |
| 3 | `CARTOGRAPHER_SCAN_CALIBRATE` → `SAVE_CONFIG` |
| 4 | `CARTOGRAPHER_TOUCH_CALIBRATE` → `SAVE_CONFIG` |
| 5 | `SHAPER_CALIBRATE` → `SAVE_CONFIG` |
| 6 | PID сопла и стола |

## G-code слайсера

Готовые блоки для **Orca Slicer** и **Bambu Studio**: `doc/slicer_gcode.md`

```gcode
; Старт
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]

; Конец
PRINT_END
```

Включите **Label objects** в настройках печати (adaptive mesh).

## Структура

```
klipper_config_mks_monster8/
├── printer.cfg            ← весь конфиг (единый файл)
└── doc/
    ├── kalico_setup.md
    ├── can0_setup.md
    └── slicer_gcode.md
```

## Макросы

| Макрос | Назначение |
|--------|------------|
| `G32` | Homing + QGL (без mesh) |
| `PRINT_START` | Старт: adaptive mesh + продувочная линия |
| `PRINT_END` | Завершение печати |
| `PURGE_LINE` | Только продувка (тест) |
| `MESH` | Ручная сетка (`MESH ADAPTIVE=1` — по объекту) |
