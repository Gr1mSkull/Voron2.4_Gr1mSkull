# G-code для слайсеров — Voron 2.4 Gr1mSkull (Kalico + Cartographer)

Старт печати разбит на три шага в **Machine G-code** Orca:

1. `PRINT_START` — homing, QGL, touch home @ 150 °C  
2. `MESH ADAPTIVE=1` — adaptive mesh **из слайсера** (видит объекты из G-code)  
3. `PRINT_BEGIN` — нагрев до печати + продувка  

В стартовый G-code **не** добавляйте: `G28`, `M190`, `M109`, `BED_MESH_CALIBRATE`, priming line.

---

## Orca Slicer

Полный набор полей — в [`orca/machine_gcode.txt`](../orca/machine_gcode.txt).

**Где:** Printer preset → **Printer Settings** → **Machine G-code**

### Machine start G-code

```gcode
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
MESH ADAPTIVE=1
PRINT_BEGIN EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

**Почему mesh в слайсере, а не в `PRINT_START`:** Moonraker вставляет `EXCLUDE_OBJECT_DEFINE` в `.gcode` **перед** стартовым блоком. Когда mesh был внутри макроса, объектов ещё не было. Отдельная строка `MESH ADAPTIVE=1` после `PRINT_START` выполняется, когда границы объектов уже в файле.

**Moonraker** (`moonraker.conf`):

```ini
[file_manager]
enable_object_processing: True
```

**Если adaptive не срабатывает** — перенесите только `MESH ADAPTIVE=1` в **Filament preset → Advanced → Start G-code** (после Machine start).

**Проверка:** в `.gcode` перед `MESH ADAPTIVE=1` должны быть строки `EXCLUDE_OBJECT_DEFINE`.

### Machine end G-code

```gcode
PRINT_END
```

### Pause / Change filament G-code

```gcode
PAUSE
```

### Printing by object / Layer change / Timelapse

Оставить **пустыми**. Удалите `TIMELAPSE_TAKE_FRAME`, `T0`, `G28` если Orca подставил из шаблона.

### Настройки Orca

| Параметр | Значение |
|----------|----------|
| G-code flavor | Klipper |
| **Others → Label objects** | **Вкл.** |
| Bed leveling | None |
| Timelapse | Выкл. (без moonraker-timelapse) |

### Ручная сетка (консоль)

```
MESH              ; полный стол
MESH ADAPTIVE=1   ; по объектам в текущем G-code
MESH SAVE=1       ; + записать в SAVE_CONFIG
```

---

## Bambu Studio

### Machine start G-code

```gcode
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
MESH ADAPTIVE=1
PRINT_BEGIN EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

### Machine end G-code

```gcode
PRINT_END
```

Label objects — включить. Печать через Fluidd/Mainsail.

---

## Проверка после слайсинга

В начале `.gcode`:

```gcode
EXCLUDE_OBJECT_DEFINE NAME=...
PRINT_START BED_TEMP=60 EXTRUDER_TEMP=240
MESH ADAPTIVE=1
PRINT_BEGIN EXTRUDER_TEMP=240
```
