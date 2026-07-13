# G-code для слайсеров — Voron 2.4 Gr1mSkull (Kalico + Cartographer)

Вся подготовка — в одном макросе **`PRINT_START`**.  
Orca передаёт границы adaptive mesh **при слайсинге** (плейсхолдеры `{adaptive_bed_mesh_*}`).

Документация Orca: [Adaptive Bed Mesh](https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_basic_information_adaptive_bed_mesh)

---

## Orca Slicer

Полный блок — в [`orca/machine_gcode.txt`](../orca/machine_gcode.txt).

### Настройка принтера (один раз)

**Printer Settings → Basic Information → Adaptive Bed Mesh** (Advanced):

| Параметр Orca | Значение |
|---------------|----------|
| `bed_mesh_min` | `30`, `30` |
| `bed_mesh_max` | `470`, `470` |
| `bed_mesh_probe_distance` | `50` (шаг точек, мм) |
| `adaptive_bed_mesh_margin` | `10` |

Margin Orca учитывает сам — в Klipper передаётся `ADAPTIVE_MARGIN=0`.

**Process → Others → Label objects** — по желанию (exclude в UI; mesh от Orca не зависит).

### Machine start G-code

```gcode
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer] MESH_MIN_X={adaptive_bed_mesh_min[0]} MESH_MIN_Y={adaptive_bed_mesh_min[1]} MESH_MAX_X={adaptive_bed_mesh_max[0]} MESH_MAX_Y={adaptive_bed_mesh_max[1]} PROBE_COUNT_X={bed_mesh_probe_count[0]} PROBE_COUNT_Y={bed_mesh_probe_count[1]} MESH_ALGO=[bed_mesh_algo]
```

**Не добавляйте:** `G28`, `M190`, `M109`, отдельный `BED_MESH_CALIBRATE`, priming line, `T0`, `TIMELAPSE_TAKE_FRAME`.

### Machine end G-code

```gcode
PRINT_END
```

### Pause / Change filament

```gcode
PAUSE
```

### Layer change / Timelapse

Установите [moonraker-timelapse](https://github.com/mainsail-crew/moonraker-timelapse) на RPi.  
В `printer.cfg` уже подключён `includes/timelapse.cfg`.

**Orca → Machine G-code → Layer change:**

```gcode
TIMELAPSE_TAKE_FRAME
```

Включение в консоли: `_SET_TIMELAPSE_SETUP ENABLE=True PARK_ENABLE=True`  
Проверка: `GET_TIMELAPSE_SETUP`

Без moonraker-timelapse оставьте поле пустым — иначе Klipper выдаст ошибку на неизвестную команду.

### Проверка после слайсинга

В `.gcode` одна строка `PRINT_START` с **числами** вместо плейсхолдеров:

```gcode
PRINT_START BED_TEMP=60 EXTRUDER_TEMP=240 MESH_MIN_X=45.2 MESH_MIN_Y=38.1 MESH_MAX_X=312.5 MESH_MAX_Y=285.0 PROBE_COUNT_X=6 PROBE_COUNT_Y=5 MESH_ALGO=bicubic
```

Если `MESH_MIN_X` и др. отсутствуют — в Orca не настроен Adaptive Bed Mesh в профиле принтера.

### Ручная сетка (консоль)

```
MESH              ; полный стол
MESH ADAPTIVE=1   ; Klipper exclude_object (без Orca)
MESH SAVE=1       ; + SAVE_CONFIG
```

---

## Bambu Studio

Тот же `PRINT_START` с плейсхолдерами Orca/Bambu, если слайсер их поддерживает; иначе укороченный вызов без mesh-параметров (полный скан из `[bed_mesh]`).

```gcode
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

```gcode
PRINT_END
```

---

## Типичные ошибки Orca

| Ошибка | Решение |
|--------|---------|
| `TIMELAPSE_TAKE_FRAME` / `T0` | Очистить шаблон Bambu в Machine G-code |
| `Extrude below minimum temp` | Убрать priming Orca — purge в `PRINT_START` |
| Mesh на весь стол | Включить Adaptive Bed Mesh в профиле принтера Orca |
