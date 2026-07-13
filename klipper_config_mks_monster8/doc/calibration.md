# Полная калибровка и подготовка к печати

**Принтер:** Voron 2.4 500×500×480  
**Плата:** MKS Monster8 V2.0 + Raspberry Pi 4B  
**Хост:** [Kalico](https://docs.kalico.gg) (не mainline Klipper)  
**Голова:** EBB SB2209 CAN (STM32G0) + Stealthburner  
**Z-проба:** Cartographer 3D (scan homing + touch mesh)  
**XY:** sensorless (TMC2209 StallGuard), 2 мотора на ось  

Конфиг: один файл `printer.cfg`. См. также `kalico_setup.md`, `can0_setup.md`, `slicer_gcode.md`.

---

## Содержание

1. [Перед началом](#1-перед-началом)
2. [Проверка связи и прошивок](#2-проверка-связи-и-прошивок)
3. [Механика и безопасность](#3-механика-и-безопасность)
4. [Калибровка XY (sensorless)](#4-калибровка-xy-sensorless)
5. [Калибровка Cartographer (scan)](#5-калибровка-cartographer-scan)
6. [Z homing и выравнивание портала (QGL)](#6-z-homing-и-выравнивание-портала-qgl)
7. [Калибровка Cartographer (touch)](#7-калибровка-cartographer-touch)
8. [Input Shaper (резонансы)](#8-input-shaper-резонансы)
9. [PID сопла и стола](#9-pid-сопла-и-стола)
10. [Дополнительно: Pressure Advance и сетка](#10-дополнительно-pressure-advance-и-сетка)
11. [Настройка слайсера](#11-настройка-слайсера)
12. [Первая печать](#12-первая-печать)
13. [Что делает каждая печать (PRINT_START)](#13-что-делает-каждая-печать-print_start)
14. [Когда перекалибровывать](#14-когда-перекалибровывать)
15. [Шпаргалка команд](#15-шпаргалка-команд)

---

## 1. Перед началом

### Что должно быть готово

- [ ] Kalico установлен, сервис `klipper` запускается
- [ ] Плагин Cartographer 3D установлен в `~/kalico` (см. `kalico_setup.md`)
- [ ] `printer.cfg` скопирован в `~/printer_data/config/`
- [ ] CAN UUID прописаны в `[mcu]`, `[mcu EBBCan]`, `[mcu cartographer]`
- [ ] Интерфейс `can0` поднят, bitrate **1000000**
- [ ] На голове есть **24V**, джампер **120Ω** на EBB
- [ ] Стол чистый, сопло не касается стекла/PEI

### Температурные ограничения Cartographer

В макросе `PRINT_START` probing идёт при **150 °C** сопла (`probe_max_temp` в `_USER_VARIABLES`).  
Не превышайте **150 °C** во время `CARTOGRAPHER_*_CALIBRATE` и touch home — иначе можно повредить пробу.

---

## 2. Проверка связи и прошивок

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
sudo systemctl start klipper
```

В Mainsail/Fluidd: **FIRMWARE_RESTART** → откройте `klippy.log`.

| Секция | Ожидаемый MCU в логе |
|--------|----------------------|
| `[mcu]` | `stm32f407xx` |
| `[mcu EBBCan]` | `stm32g0b1xx` |
| `[mcu cartographer]` | `CARTOGRAPHER 5.x.x` |

Ошибок `MCU Protocol error`, `tmcuart_send`, `gpio20` быть не должно.  
При проблемах — `can0_setup.md`.

Базовые команды в консоли:

```
STATUS
QUERY_ENDSTOPS
```

---

## 3. Механика и безопасность

Выполните **до** электронной калибровки:

| Проверка | Действие |
|----------|----------|
| Ремни XY | Натянуты одинаково, без провисания |
| Ремни Z (×4) | Натянуты, винты на шкивах затянуты |
| Все 4 Z-мотора | Крутятся в одну сторону при ручном подъёме портала |
| Каретки / рельсы | Нет заеданий, посторонних звуков |
| Сопло | Чистое, не болтается |
| Cartographer | Закреплён жёстко, провод CAN не натянут |

При первом включении Z проверьте направление: портал должен **подниматься** при homing.  
Если едет вниз — инвертируйте `dir_pin` на всех `stepper_z*` (см. комментарии в `printer.cfg`).

---

## 4. Калибровка XY (sensorless)

Физических концевиков X/Y нет — срабатывание через **TMC StallGuard**.

Текущие значения в конфиге:

| Ось | `driver_SGTHRS` | `diag_pin` |
|-----|-----------------|------------|
| X | 80 | `^PA14` |
| Y | 115 | `^PA15` |

### Подбор чувствительности

```
SGTHRS_TEST AXIS=X VALUE=80
G28 X
```

Если ось **не доезжает** до края (ложное срабатывание) — **уменьшите** VALUE (например 70).  
Если **врезается** в раму — **увеличьте** VALUE (например 90).

Для Y:

```
SGTHRS_TEST AXIS=Y VALUE=115
G28 Y
```

Диапазон подбора обычно **60–130**. Y часто выше X.

После подбора впишите итоговые значения в `[tmc2209 stepper_x]` / `stepper_y` в `printer.cfg`  
или используйте `SET_TMC_FIELD` и `SAVE_CONFIG` (если Klipper сохранит поле).

### Проверка XY

```
G28 X Y
```

Портал перед XY **поднимается на 15 мм** (макрос `G28`).  
Координаты после homing: X=500, Y=500 (конец хода).

Если Y едет «не туда» — добавьте/уберите `!` у `dir_pin` в `[stepper_y]`.

---

## 5. Калибровка Cartographer (scan)

Scan-модель нужна для **G28 Z** (бесконтактный homing по катушке).

> Если внизу `printer.cfg` уже есть блок `[cartographer scan_model default]` в SAVE_CONFIG —  
> шаг можно **пропустить**, если не меняли пробу, сопло или прошивку Cartographer.

### Порядок

1. `FIRMWARE_RESTART`
2. `G28 X Y`
3. `CARTOGRAPHER_SCAN_CALIBRATE`

Процедура в консоли:

- Принтер просканирует стол
- Появится **paper test** — подстройте Z бумажным тестом:
  ```
  TESTZ Z=-0.01
  TESTZ Z=0.01
  ACCEPT
  ```
4. **`SAVE_CONFIG`** — модель запишется в конец `printer.cfg`

Подсказка в консоли: `CARTO_CALIBRATE`

### Проверка

```
G28 Z
```

Ошибки `Scan model not loaded` быть не должно.

---

## 6. Z homing и выравнивание портала (QGL)

Voron 2.4 — **quad gantry**. Портал нужно выровнять по четырём углам.

### Порядок

```
G28 X Y
G28 Z
QUAD_GANTRY_LEVEL
G28 Z
```

Или одной командой (без mesh):

```
G32
```

`G32` делает: очистка mesh → G28 XY → QGL → G28 Z → парковка в центр на Z30.

### Что смотреть

- Все 4 точки QGL проходят без ошибок
- `retry_tolerance: 0.0075` — при частых retry проверьте механику Z
- После QGL снова **G28 Z** обязателен

---

## 7. Калибровка Cartographer (touch)

Touch-модель используется для **точной сетки стола** и `CARTOGRAPHER_TOUCH_HOME` в `PRINT_START`.

> Если блок `[cartographer touch_model default]` уже в SAVE_CONFIG — пропустите,  
> если первый слой после печати в норме.

### Порядок

1. `G28 X Y`
2. `G28 Z`
3. `QUAD_GANTRY_LEVEL`
4. `G28 Z`
5. Нагрейте сопло до **150 °C** (не выше):
   ```
   M104 S150
   ```
6. `CARTOGRAPHER_TOUCH_CALIBRATE`
7. **`SAVE_CONFIG`**

### Проверка touch home

```
G28
QUAD_GANTRY_LEVEL
G28 Z
M104 S150
M109 S150
CARTOGRAPHER_TOUCH_HOME
```

Сопло мягко касается стола в точке home — без ударов и ошибок.

---

## 8. Input Shaper (резонансы)

Акселерометр **ADXL345** на Cartographer (V3: `PA3`).

### Условия

- Принтер на твёрдой поверхности
- Ремни натянуты, болты проверены
- Сопло остыло или ≤50 °C (чтобы не мешать вибрациям)

### Команда

```
SHAPER_CALIBRATE
```

Дождитесь завершения тестов по X и Y → **`SAVE_CONFIG`**.

В SAVE_CONFIG появится секция `[input_shaper]` с `shaper_type_x/y` и `shaper_freq_x/y`.

Повторяйте после: замены ремней, смены массы головы, крупного тюнинга рамы.

---

## 9. PID сопла и стола

### Сопло (рекомендуется 240 °C для PA/PLA+)

```
PID_CALIBRATE HEATER=extruder TARGET=240
```

Дождитесь окончания (несколько минут) → **`SAVE_CONFIG`**.

### Стол

```
PID_CALIBRATE HEATER=heater_bed TARGET=60
```

Для ABS/ASA можно повторить с `TARGET=100`. → **`SAVE_CONFIG`**

---

## 10. Дополнительно: Pressure Advance и сетка

### Pressure Advance

В конфиге стартовое значение: `pressure_advance: 0.04` (Bambu X1C hotend 0.4 mm).

Тонкая настройка — тестовая башня или паттерн в Orca Slicer:

```
SET_PRESSURE_ADVANCE ADVANCE=0.04
```

После подбора впишите значение в `[extruder]` и сохраните файл.

### Полная сетка стола (ручная)

Для проверки без печати:

```
G28
QUAD_GANTRY_LEVEL
G28 Z
M104 S150
M109 S150
CARTOGRAPHER_TOUCH_HOME
MESH
```

`MESH` — полный стол. `MESH ADAPTIVE=1` — только зона объектов (нужен Label objects в слайсере).

Визуализируйте mesh в Mainsail → **Bed Mesh**.

---

## 11. Настройка слайсера

Подробно: **`slicer_gcode.md`**.

### Минимум

**Machine start G-code:**

```gcode
PRINT_START BED_TEMP=[bed_temperature_initial_layer_single] EXTRUDER_TEMP=[nozzle_temperature_initial_layer]
```

**Machine end G-code:**

```gcode
PRINT_END
```

### Обязательно включить

- **Label objects** (Orca / Bambu: Print settings → Others) — для adaptive mesh
- Размер стола **500×500**, центр **250, 250**

### Не добавлять в слайсер

- `G28`, `M190`, `M109` — уже внутри `PRINT_START`
- `BED_MESH_CALIBRATE` — уже в `PRINT_START`
- Свою priming line — продувка в `_PURGE_LINE`

---

## 12. Первая печать

### Чеклист перед стартом

- [ ] Полная калибровка (разделы 4–9) выполнена или SAVE_CONFIG актуален
- [ ] Филамент загружен, датчик runout работает
- [ ] Стол чистый (спирт / мыльная вода для PEI)
- [ ] Слайсер: `PRINT_START` / `PRINT_END`, Label objects включён
- [ ] Тестовая модель: калибровочный куб 20×20×20 или первый слой

### Запуск

1. Загрузите G-code в Mainsail/Fluidd
2. Проверьте температуры в начале файла:
   ```gcode
   PRINT_START BED_TEMP=60 EXTRUDER_TEMP=240
   ```
3. **Print** — не прерывайте первые ~15 минут (homing, QGL, mesh, purge)

### Тест только продувки (без печати)

```
G28
PURGE_LINE
```

Координаты линии: X 50→150, Y=20 (настраивается в `_USER_VARIABLES`).

Лимит Klipper: `max_extrude_cross_section = 4 × nozzle²` → для 0.4 мм сопла **0.640 mm²**.  
Старая настройка `purge_extrude: 35` на линии 100 мм давала **0.842 mm²** и ошибку при старте.  
Макрос `_PURGE_LINE` автоматически ограничивает E; по умолчанию `purge_extrude: 26`.

---

## 13. Что делает каждая печать (PRINT_START)

Макрос `PRINT_START` выполняет автоматически:

| Шаг | Действие |
|-----|----------|
| 1 | Подсветка `LIGHTS_ON` |
| 2 | Сброс Z-offset, очистка mesh |
| 3 | `G28` (Z-hop → XY → Z) |
| 4 | Нагрев стола → ожидание `M190` |
| 5 | `QUAD_GANTRY_LEVEL` |
| 6 | `G28 Z` |
| 7 | Нагрев сопла до 150 °C → `M109` |
| 8 | `CARTOGRAPHER_TOUCH_HOME` |
| 9 | `BED_MESH_CALIBRATE` — adaptive если объекты уже в G-code, иначе полный скан |
| 10 | Нагрев сопла до рабочей температуры |
| 11 | Продувочная линия `_PURGE_LINE` |
| 12 | Парковка в центр стола |

`PRINT_END`: retract, парковка Y=480, вытяжка + Nevermore на 10 мин.

---

## 14. Когда перекалибровывать

| Событие | Что перекалибровать |
|---------|---------------------|
| Смена сопла / хотенда | Touch (`CARTOGRAPHER_TOUCH_CALIBRATE`), возможно scan |
| Снятие/перестановка Cartographer | Scan + touch, проверить `x_offset` / `y_offset` |
| Замена стекла / PEI | Touch, тест первого слоя |
| Ослабление ремней XY | `SGTHRS_TEST`, Input Shaper |
| Регулировка Z-винтов, QGL часто retry | `QUAD_GANTRY_LEVEL`, touch |
| Обновление прошивки Cartographer | Scan (если попросит), touch |
| Раз в 1–3 месяца | Input Shaper, PID при смене сезона |

Scan/touch модели в SAVE_CONFIG **не слетают** при обычном `FIRMWARE_RESTART`.

---

## 15. Шпаргалка команд

### Первичная калибровка (с нуля)

```
FIRMWARE_RESTART
G28 X Y
CARTOGRAPHER_SCAN_CALIBRATE
; paper test → ACCEPT → SAVE_CONFIG
G28 Z
QUAD_GANTRY_LEVEL
G28 Z
M104 S150
CARTOGRAPHER_TOUCH_CALIBRATE
SAVE_CONFIG
SHAPER_CALIBRATE
SAVE_CONFIG
PID_CALIBRATE HEATER=extruder TARGET=240
SAVE_CONFIG
PID_CALIBRATE HEATER=heater_bed TARGET=60
SAVE_CONFIG
```

### Быстрая подготовка к печати (уже откалиброван)

```
G32
```

или просто запуск печати — `PRINT_START` сделает всё сам.

### Полезные макросы

| Команда | Назначение |
|---------|------------|
| `G32` | Homing + QGL + Z |
| `CARTO_CALIBRATE` | Подсказка по шагам Cartographer |
| `MESH` / `MESH ADAPTIVE=1` | Ручная сетка |
| `PURGE_LINE` | Тест продувки |
| `SGTHRS_TEST AXIS=Y VALUE=115` | Подбор sensorless |
| `LIGHTS_ON` / `LIGHTS_OFF` | Подсветка камеры |

### Типичные ошибки

| Ошибка | Решение |
|--------|---------|
| `Scan model not loaded` | `CARTOGRAPHER_SCAN_CALIBRATE` → `SAVE_CONFIG` |
| Портал опускается на XY homing | Проверить `dir_pin` Z, макрос `G28` |
| Первый слой слишком высокий/низкий | `CARTOGRAPHER_TOUCH_CALIBRATE` → `SAVE_CONFIG` |
| QGL не сходится | Механика Z, затем повторить QGL |
| Sensorless не ловит край | `SGTHRS_TEST`, подобрать VALUE |
| Mesh на весь стол вместо детали | Включить **Label objects** в слайсере |

---

*Документ для конфигурации `klipper_config_mks_monster8/printer.cfg` (Gr1mSkull Voron 2.4).*
