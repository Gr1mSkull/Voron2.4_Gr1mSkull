# G-code для слайсеров — Voron 2.4 Gr1mSkull (Kalico + Cartographer)

Вся подготовка (homing, QGL, touch home, **adaptive mesh**, продувка) — в макросе `PRINT_START`.
В стартовый G-code слайсера **не** добавляйте: `G28`, `M190`, `M109`, `BED_MESH_CALIBRATE`, линию priming.

---

## Orca Slicer

**Где:** Printer Settings → Machine G-code

### Machine start G-code

```gcode
; Voron 2.4 Gr1mSkull — Kalico + Cartographer
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

Если плейсхолдеры не подставляются (старая версия Orca), попробуйте:

```gcode
PRINT_START BED_TEMP={bed_temperature_initial_layer[current_extruder]} EXTRUDER_TEMP={nozzle_temperature_initial_layer[current_extruder]}
```

### Machine end G-code

```gcode
PRINT_END
```

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
