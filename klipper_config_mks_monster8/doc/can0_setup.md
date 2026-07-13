# CAN bus — MKS Monster8 V2.0 + RPi 4B (Kalico @ 1000000)

> Прошивки MCU собирайте из **~/kalico**, не из ~/klipper.
> Установка Kalico и плагина Cartographer: `doc/kalico_setup.md`
>
> **Эта сборка:** EBB SB2209 CAN на **STM32G0B1** (не RP2040). Пины в `printer.cfg` — `PD0`, `PA15`, `PB13` и т.д.

## 0. Диагностика UUID (читать первым при ошибках ADC / pin)

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
```

После `FIRMWARE_RESTART` в **klippy.log** для каждой секции смотрите строку `MCU '…' config: MCU=…`:

| Секция в printer.cfg | Должно быть в логе | НЕ должно быть |
|----------------------|-------------------|----------------|
| `[mcu]` | `MCU=stm32f407xx` | `stm32g0b1xx`, `CARTOGRAPHER` |
| `[mcu EBBCan]` | `MCU=stm32g0b1xx` | `stm32f407`, `CANBUS_BRIDGE=1`, `CARTOGRAPHER`, `rp2040` |
| `[mcu cartographer]` | `CARTOGRAPHER` | `stm32f407`, `stm32g0b1xx` |

### Ошибка `Pin 'gpio20' is not a valid pin name on mcu 'EBBCan'`

В `printer.cfg` **не должно быть** пинов `gpio*`. Если ошибка появляется — почти всегда **неверный UUID в `[mcu EBBCan]`** (в слот попал Cartographer или другая плата).

#### Шаг 1 — UUID на шине

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
sudo systemctl start klipper
```

Типичный вывод (3 устройства):

```
Found canbus_uuid=xxxxxxxx, Application: Klipper   ← Monster8 → [mcu]
Found canbus_uuid=yyyyyyyy, Application: Klipper   ← EBB STM32G0 → [mcu EBBCan]
Found canbus_uuid=zzzzzzzz, Application: Klipper   ← Cartographer → [mcu cartographer]
```

> Если EBB **не в списке** — питание 24V на голову, CAN-кабель, джампер 120Ω на EBB, прошивка Katapult/Kalico на EBB.

#### Шаг 2 — что пишет лог для EBBCan

| `MCU 'EBBCan' config:` | Причина | Действие |
|------------------------|---------|----------|
| `MCU=stm32g0b1xx` | OK для этой сборки | UUID верный |
| `MCU=stm32f407xx CANBUS_BRIDGE=1` | В EBB слот попал UUID Monster8 | Поменять UUID местами с `[mcu]` |
| `MCU=… CARTOGRAPHER` | UUID Cartographer в EBB | Cartographer → `[mcu cartographer]` |
| `MCU=rp2040` | Чужая прошивка / не та плата | Перепрошить EBB как STM32G0 (§4) |
| Нет строки / timeout | EBB не на шине | Питание, CAN, прошивка |

#### Шаг 3 — проверка

`FIRMWARE_RESTART` → в логе три строки:

```
MCU 'mcu' config: MCU=stm32f407xx
MCU 'EBBCan' config: MCU=stm32g0b1xx
MCU 'cartographer' config: … CARTOGRAPHER …
```

### Ошибка `MCU Protocol error` / `Unknown command: tmcuart_send` на EBBCan

Kalico на Pi **не совместим** с прошивкой mainline Klipper на MCU. Плюс UUID могут быть перепутаны.

#### Как читать сообщение об ошибке

Строка `MCU(s) which should be updated` — **какая прошивка сейчас на каком слоте** в `printer.cfg`:

| Слот в printer.cfg | Версия в ошибке | Что это за плата | Куда UUID |
|--------------------|-----------------|------------------|-----------|
| `mcu` | `v0.12.0-…` (Klipper) | Monster8 F407 | UUID Monster8 → `[mcu]` |
| `EBBCan` | `CARTOGRAPHER 5.0.0` | **Cartographer** (перепутан!) | UUID Cartographer → `[mcu cartographer]` |
| `cartographer` | `v0.12.0-…` (Klipper) | **EBB STM32G0** (перепутан!) | UUID EBB → `[mcu EBBCan]` |

**Исправление UUID:** EBB UUID в `[mcu EBBCan]`, Cartographer UUID в `[mcu cartographer]`.

#### Прошивки под Kalico

| Слот | Нужная прошивка | Откуда |
|------|-----------------|--------|
| `[mcu]` | Kalico, STM32F407 | `~/kalico` (§1) |
| `[mcu EBBCan]` | Kalico, STM32G0B1 CAN | `~/kalico` (§4) |
| `[mcu cartographer]` | **CARTOGRAPHER** (своя) | `~/cartographer_firmware` — **не Kalico** |

Cartographer **не** прошивается Kalico — в слоте `cartographer` версия `CARTOGRAPHER x.x.x` это нормально.

```bash
# Monster8 + EBB — сборка из Kalico
cd ~/kalico && make menuconfig   # F407 bridge или CAN — см. §1
make clean && make
# прошивка по CAN/USB — см. §1 и §4

# Cartographer — отдельно
# https://docs.cartographer3d.com/cartographer-probe/firmware
```

После прошивки `FIRMWARE_RESTART` — в логе **нет** `MCU Protocol error`, версии MCU совпадают с Kalico (кроме cartographer).

```
MCU 'mcu' config: MCU=stm32g0b1xx        ← в [mcu] UUID от UTOC/U2C (G0B1)
MCU 'EBBCan' config: MCU=stm32f407xx CANBUS_BRIDGE=1  ← Monster8 в слоте EBB
MCU 'mcu' shutdown: Not a valid ADC pin  ← пины Monster8 ушли на чужой чип
```

**Причина:** UUID перепутаны. Пины `PC0`, `PE6`, `PA0`… относятся к **Monster8 F407**, а не к G0B1.

**Исправление:**
1. `canbus_query.py can0` — список UUID на шине
2. UUID с **stm32f407** (Monster8) → `[mcu]`
3. UUID с **stm32g0b1xx** (EBB) → `[mcu EBBCan]`
4. UUID Cartographer → `[mcu cartographer]`
5. **G0B1 / UTOC / U2C** — не прописывать в `[mcu]` (это USB↔CAN адаптер, не плата принтера)

---

## 1. Два варианта подключения Monster8

### Вариант A — Monster8 как USB-CAN мост (can0 на Pi через USB Monster8)

Monster8 прошит **USB to CAN bus bridge**. Pi видит `can0` через USB.  
На CAN-шине Monster8 может быть доступен как `[mcu]` по своему UUID (проверьте `canbus_query`).

**Kalico menuconfig (Monster8 V2.0):**
- MCU: STM32F407
- Bootloader offset: **48KiB**
- Clock: 8 MHz crystal
- Communication: **USB to CAN bus bridge (USB on PA11/PA12)**
- CAN speed: **1000000**

### Вариант B — отдельный USB-CAN (UTOC/U2C) + Monster8 на CAN (как deflord/3def)

Адаптер G0B1 даёт `can0` на Pi. Monster8 прошит **CAN bus** (не bridge):

**Kalico menuconfig (Monster8 V2.0):**
- MCU: STM32F407
- Bootloader offset: **48KiB**
- Communication: **CAN bus (on PB8/PB9)** или по разводке платы
- CAN speed: **1000000**

В `[mcu]` — UUID Monster8 с `MCU=stm32f407xx`.

---

## 2. Пины корпуса Monster8 (только для `[mcu]` = F407)

> PB0/PB1 зарезервированы под CAN в bridge-режиме.
> Nevermore PB0 (`temperature_fan`, датчик PC0) | вытяжка PA3 | апп.отсек PA0 (`temperature_host`) | подсветка PA8 (см. `printer.cfg`).

### Температура Monster8 / апп. отсека

`temperature_mcu` (`ADC_TEMPERATURE`) на `[mcu]` в CAN-конфигурации часто даёт ошибку или конфликт с `controller_fan`.  
В `printer.cfg`: `[temperature_sensor Monster8]` и `[temperature_fan controller_fan]` используют **`temperature_host`** (температура RPi в том же отсеке). `target_temp: 50` для вентилятора — ориентир под CPU Pi, не под кристалл F407.

## 3. Интерфейс can0 (MainsailOS)

Файл `/etc/network/interfaces.d/can0`:

```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 1024
```

```bash
sudo ifup can0
ip -details link show can0
```

## 4. Прошивка EBB SB2209 CAN (STM32G0B1)

На плате чип **STM32G0**. В логе: `MCU 'EBBCan' config: MCU=stm32g0b1xx`.

**Kalico menuconfig:**
- MCU: STM32G0B1
- Clock: 8 MHz crystal
- Communication: **CAN bus (on PD0/PD1)** или по silkscreen платы
- CAN speed: **1000000**
- Bootloader offset: **8KiB** (Katapult)

```bash
sudo systemctl stop klipper
cd ~/kalico
make menuconfig   # STM32G0B1 + CAN @ 1M
make clean && make
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/kalico/out/klipper.bin -u REPLACE_EBB_UUID
```

Пины в `printer.cfg`: `PD0`/`PD1` extruder, `PA15` UART TMC, `PB13` heater, `PA1` part fan и т.д.

## 5. Прошивка Cartographer

Отдельный репозиторий `~/cartographer_firmware`. См. https://docs.cartographer3d.com

## 6. Терминаторы 120 Ω

- Monster8 (если конец шины)
- EBB SB2209 (джампер 120R)
- Cartographer (если конец шины)

## 7. Проверка

`FIRMWARE_RESTART`, в логе — правильные `MCU=…` для трёх секций, затем `QUERY_ENDSTOPS`, `STATUS`.
