# Периферия (эталон 3Def SB2040V3/500)

Всё в **одном** `printer.cfg` — без `[include]` и **без модуля вкл/выкл** (offmodule / `SHUT_DOWN`).

Адаптация: **MKS Monster8 V2** + **EBB SB2209 CAN** + **Cartographer 3D** (вместо Klicky/SB2040 в эталоне).

| Модуль | Секция в printer.cfg | Пины / примечания |
|--------|----------------------|-------------------|
| Таймлапс | `# ТАЙМЛАПС` | moonraker-timelapse, см. `doc/timelapse_setup.md` |
| Очистка сопла | `# ОЧИСТКА СОПЛА` | `clean_nozzle`, щётка X≈380 Y≈356 (500 мм) |
| StealthBurner LED | `# STEALTHBURNER LED` | `sb_leds` на `EBBCan:PD3` |
| Подсветка камеры | `onled` / `offled` | `Подсветка` PA8 + sb_leds |
| Nevermore | `NEVERMORE_ON/OFF` | `temperature_fan nevermore` PB0 |
| Датчик филамента | `[filament_motion_sensor Пластик]` | PB12 |
| Старт/конец | `PRINT_START` / `PRINT_END` | 3Def + Orca adaptive mesh + Cartographer touch |

## Установка на принтер

```bash
rm -rf ~/printer_data/config/includes/
cp printer.cfg ~/printer_data/config/
FIRMWARE_RESTART
```

Если была ошибка `gcode_macro shut_down` / `mcu` — удалите старый `includes/offmodule.cfg` и блоки `SHUT_DOWN` из `SAVE_CONFIG` на Pi.

## Датчик филамента

Motion sensor на **PB12** Monster8 (`detection_length: 22`).  
В `PRINT_START` датчик временно отключается; при runout — `PAUSE` + бипер.

Если установлен switch на EBB (`EBBCan:PB8`) — замените секцию `[filament_motion_sensor Пластик]` в `printer.cfg`.

## Очистка сопла

Ручной вызов: `clean_nozzle`, `CLEAN_NOPURGE`, `CLEAN_PRIME`, `CLEAN_PURGE`, `CLEAN_HOTCOLD`.

Координаты щётки/ведёрок — в макросе `clean_nozzle` (`variable_brush_start`, `variable_bucket_start` и т.д.).

## Пересборка конфига

Исходники 3Def встроены в репозиторий; для регенерации:

```bash
python3 klipper_config_mks_monster8/build_printer_cfg.py
```
