# Voron 2.4 StealthChanger — конфигурация (второй принтер)

Альтернативная «ветка» для **второго** принтера с тулченджером StealthChanger.

**Сборка:** 500×500×480 | Manta M8P v2.0 + CB2 (образ BTT CB2 V3.0.2 — Debian 12) | 6× EBB SB2209 CAN (RP2040) |
Phaetus Rapido (PT1000) | OptoTap на каждой голове | Nudge (калибровка XY) |
klipper-toolchanger-easy

> Это отдельная папка, не зависящая от `klipper_config/` (первый принтер).
> При желании позже можно вынести в отдельную git-ветку/репозиторий.

## Быстрый старт

Полная инструкция — `doc/stealthchanger_setup.md`. Кратко:

1. Настроить CAN @ 1000000 (7 узлов).
2. Прошить M8P (CAN bridge) и 6× SB2209 (CAN), получить UUID.
3. Установить `klipper-toolchanger-easy` (`install.sh`).
4. Скопировать `stealthchanger_config/*` в `~/printer_data/config/`
   (сохранив `toolchanger/readonly-configs/`, созданный install.sh).
5. Вписать UUID, координаты доков, пин Nudge.
6. Калибровка по инструкции.

## Структура

```
stealthchanger_config/
├── printer.cfg              → база + include тулченджера
├── mcu.cfg                  → Manta M8P (CAN)
├── printer_base.cfg
├── endstops/
│   ├── endstops_xy_physical.cfg     ← по умолчанию (концевики на раме)
│   └── endstops_xy_sensorless.cfg
├── steppers/steppers_z.cfg          → 4× Z, Z homing = OptoTap
├── heater/heater_bed.cfg            → AC SSR
├── fans/fans.cfg                    → рама (part/hotend fan — на головах)
├── homing/quad_gantry_level.cfg
├── macros/macros.cfg                → PRINT_START/END под тулченджер
├── toolchanger/
│   ├── toolchanger-config.cfg       → оверрайды: homing, Nudge, tools_calibrate
│   └── tools/
│       └── T0.cfg … T5.cfg          → 6 голов (SB2209, Rapido PT1000, OptoTap)
└── doc/stealthchanger_setup.md
```
> `toolchanger/readonly-configs/` создаёт `install.sh` — в репозиторий не входит.

## Переключатели

### XY homing — physical / sensorless

В `printer.cfg`:
```ini
[include endstops/endstops_xy_physical.cfg]
# [include endstops/endstops_xy_sensorless.cfg]
```
И синхронно в `toolchanger/toolchanger-config.cfg`:
```ini
[gcode_macro homing_override_config]
variable_sensorless_x: False   # True для sensorless
variable_sensorless_y: False
variable_homing_rebound_y: 0   # 20 для sensorless
```

## Отличия от первого принтера

| | Принтер 1 | Принтер 2 (StealthChanger) |
|---|---|---|
| Голова | 1× фикс. (CW2/SB) | 6× сменных (StealthChanger) |
| Toolboard | 1× SB2209 | 6× SB2209 (EBBT0..T5) |
| Хотенд | Bambu X1C | Rapido (PT1000) |
| Z-проба | Voron Tap | OptoTap на каждой голове |
| XY offsets | — | Nudge (tools_calibrate) |
| Кинематика | corexy (+опц. AWD) | corexy |
| X endstop | на toolhead | на раме (M8P) |
| Софт | стандартный Klipper | + klipper-toolchanger-easy |

## Важные замечания

- **При старте голова должна быть на шаттле** (`require_tool_present: True`,
  Z-проба = OptoTap активной головы), иначе Klipper уйдёт в shutdown.
- **Всегда** `G28` / `QUAD_GANTRY_LEVEL` / `BED_MESH` с **T0**.
- **`SAVE_CONFIG` не используется** для оффсетов тулов — вписывайте вручную в `Tx.cfg`.
- Одновременно допустим только **один** `[adxl345]` — раскомментируйте акселерометр
  только у калибруемой головы.
- **PT1000 (Rapido):** проверьте пуллап на плате; при необходимости
  раскомментируйте `pullup_resistor` в `Tx.cfg`.
