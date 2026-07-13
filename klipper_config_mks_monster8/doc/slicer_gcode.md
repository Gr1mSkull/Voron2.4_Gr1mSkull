# G-code для слайсеров — Voron 2.4 Gr1mSkull (Kalico + Cartographer)

Вся подготовка (homing, QGL, touch home, **adaptive mesh**, продувка) — в макросе `PRINT_START`.
В стартовый G-code слайсера **не** добавляйте: `G28`, `M190`, `M109`, `BED_MESH_CALIBRATE`, линию priming.

---

## Orca Slicer (актуальные плейсхолдеры)

Полный набор полей — в [`orca/machine_gcode.txt`](../orca/machine_gcode.txt).

**Где:** Printer preset → **Printer Settings** → **Machine G-code**

### Machine start G-code

```gcode
M117 ; Moonraker: EXCLUDE_OBJECT до PRINT_START (нужно для adaptive mesh)
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

**Почему `M117`:** Moonraker часто вставляет `EXCLUDE_OBJECT_DEFINE` **после** первой строки стартового G-code. Без `M117` в `PRINT_START` ещё нет объектов → `BED_MESH_CALIBRATE ADAPTIVE=1` не строит сетку. Макрос автоматически переключится на полный скан, но adaptive не сработает.

**Moonraker** (`moonraker.conf`):

```ini
[file_manager]
enable_object_processing: True
```

Синтаксис Orca 2.3+ (векторные плейсхолдеры — для Filament → Advanced или если `[]` не подставляются):

```gcode
PRINT_START BED_TEMP={bed_temperature_initial_layer[initial_extruder]} EXTRUDER_TEMP={nozzle_temperature_initial_layer[initial_extruder]}
```

**Не добавляйте** в start: `G28`, `M190`, `M109`, `BED_MESH_CALIBRATE`, линию priming — всё это уже в `PRINT_START`.

### Machine end G-code

```gcode
PRINT_END
```

### Pause G-code

```gcode
PAUSE
```

### Change filament G-code

```gcode
PAUSE
```

### Printing by object / Layer change / Timelapse

Оставить **пустыми** (adaptive mesh один раз в `PRINT_START`).

### Настройки профиля принтера (Orca)

| Параметр | Значение |
|----------|----------|
| Bed shape | 500 × 500 mm |
| Origin | левый передний угол (0, 0) |
| G-code flavor | Klipper |
| Host type | OctoPrint / Klipper (Moonraker) |

### Настройки процесса (Process)

| Параметр | Значение |
|----------|----------|
| **Others → Label objects** | **Вкл.** (обязательно для adaptive mesh) |
| Bed leveling type | **None** (уровень в Kalico) |
| Timelapse / Smooth mode purge | **Выкл.** (purge в `PRINT_START`) |
| Skirt | по желанию; не как единственный priming |

### Для adaptive mesh (обязательно)

**Print settings → Others → Label objects** — включить.

Без этого `BED_MESH_CALIBRATE ADAPTIVE=1` просканирует весь стол.

### Что отключить в профиле Orca

- Собственная калибровка стола / bed leveling в слайсере
- Priming line / skirt только для прогрева (продувка уже в `PRINT_START`)
- Дублирующий `G28` в Machine start

---

## Bambu Studio (сторонний принтер / Klipper)

**Где:** Printer Settings → Machine G-code  
(профиль «Custom» / Voron, хост — Klipper через Moonraker)

### Machine start G-code

```gcode
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

### Machine end G-code

```gcode
PRINT_END
```

### Для adaptive mesh

**Print settings → Others → Label objects** — включить.

### Bambu Studio + Moonraker

Печать через Fluidd/Mainsail (не с флешки Bambu). В профиле принтера укажите размер стола **500×500**, центр **250, 250**.

---

## Пауза / отмена (опционально)

Если слайсер вызывает стандартные команды — в Kalico уже есть макросы `PAUSE` / `RESUME` / `CANCEL_PRINT`.

Orca / Bambu **Machine pause G-code** (при необходимости):

```gcode
PAUSE
```

**Machine resume G-code:**

```gcode
RESUME
```

---

## Проверка

После слайсинга откройте `.gcode` — в начале файла должно быть:

```gcode
PRINT_START BED_TEMP=60 EXTRUDER_TEMP=240
```

(числа из настроек филамента, не плейсхолдеры в квадратных скобках).
