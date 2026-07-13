# Периферия (эталон 3Def SB2040V3/500)

Всё в **`printer.cfg`** — адаптировано под **MKS Monster8 V2** + **EBB SB2209 CAN**.

| Модуль | Секция в printer.cfg | Пины / примечания |
|--------|----------------------|-------------------|
| Таймлапс | `# ТАЙМЛАПС` | moonraker-timelapse, см. `doc/timelapse_setup.md` |
| Очистка сопла | `# ОЧИСТКА СОПЛА` | `clean_nozzle`, щётка X≈380 Y≈356 (500 мм) |
| StealthBurner LED | `# STEALTHBURNER LED` | `sb_leds` на `EBBCan:PD3` |
| Подсветка камеры | `onled` / `offled` | `Подсветка` PA8 + sb_leds |
| Nevermore | `NEVERMORE_ON/OFF` | `temperature_fan nevermore` PB0 |
| Выкл. модуль | `# МОДУЛЬ ВКЛ/ВЫКЛ` | `DWGJ_ON` → `PRINT_END` → `M81` → PC5 |
| Датчик филамента | `[filament_motion_sensor Пластик]` | PB12 |
| Пауза / загрузка | `# ПАУЗА` | `LOAD_FILAMENT`, `UNLOAD_FILAMENT` |

## Автоотключение

Перед печатью (если нужно выключить принтер после job):

```
DWGJ_ON
```

Отмена:

```
DWGJ_OFF
```

`PRINT_END` запускает отложенный `powerOFF` (300 с) — срабатывает только при активном `DWGJ_ON`.

## Датчик филамента

Motion sensor на **PB12** Monster8 (`detection_length: 22`).  
В `PRINT_START` датчик временно отключается; при runout — пауза + бипер.

Если установлен switch на EBB (`EBBCan:PB8`) — замените секцию в `filament_sensor.cfg` на `[filament_switch_sensor Пластик]`.

## Очистка сопла

Ручной вызов: `clean_nozzle`, `CLEAN_NOPURGE`, `CLEAN_PRIME`, `CLEAN_PURGE`, `CLEAN_HOTCOLD`.

Координаты щётки/ведёрок — в начале `nozzle_scrub.cfg` (`variable_brush_start`, `variable_bucket_start` и т.д.).
