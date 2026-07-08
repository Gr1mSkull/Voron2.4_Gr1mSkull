# CAN bus — MKS Monster8 V2.0 + RPi 4B (Kalico @ 1000000)

> Прошивки MCU собирайте из **~/kalico**, не из ~/klipper.
> Установка Kalico и плагина Cartographer: `doc/kalico_setup.md`

## 0. Диагностика UUID (читать первым при ошибках ADC / pin)

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
```

После `FIRMWARE_RESTART` в **klippy.log** для каждой секции смотрите строку `MCU '…' config: MCU=…`:

| Секция в printer.cfg | Должно быть в логе | НЕ должно быть |
|----------------------|-------------------|----------------|
| `[mcu]` | `MCU=stm32f407xx` | `stm32g0b1xx`, `rp2040`, `CARTOGRAPHER` |
| `[mcu EBBCan]` | `MCU=rp2040` (Kalico) | `stm32g0b1`, `stm32f407`, `CANBUS_BRIDGE=1` |

### Ошибка `Pin 'gpio20' is not a valid pin name on mcu 'EBBCan'`

Пины `gpio18`, `gpio20`… работают **только** если в логе:

```
MCU 'EBBCan' config: MCU=rp2040
```

Если `mcu` уже `stm32f407xx`, а EBB падает на `gpio20` — почти всегда **неверный UUID в `[mcu EBBCan]`**.

#### Шаг 1 — UUID на шине

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
sudo systemctl start klipper
```

Типичный вывод (3 устройства):

```
Found canbus_uuid=xxxxxxxx, Application: Klipper   ← Monster8 → [mcu]
Found canbus_uuid=yyyyyyyy, Application: Klipper   ← EBB RP2040 → [mcu EBBCan]
Found canbus_uuid=zzzzzzzz, Application: Klipper   ← Cartographer → [mcu cartographer]
```

> Если EBB **не в списке** — питание 24V на голову, CAN-кабель, джампер 120Ω на EBB, прошивка Katapult/Klipper на EBB.

#### Шаг 2 — что пишет лог для EBBCan

| `MCU 'EBBCan' config:` | Причина | Действие |
|------------------------|---------|----------|
| `MCU=rp2040` | Редко: прошивка не Kalico RP2040 | Перепрошить EBB из `~/kalico` (§4) |
| `MCU=stm32g0b1xx` | UUID от UTOC/U2C или чужой G0 | Поставить UUID **EBB** из `canbus_query` |
| `MCU=stm32f407xx CANBUS_BRIDGE=1` | В EBB слот попал UUID Monster8 | Поменять UUID местами с `[mcu]` |
| `MCU=… CARTOGRAPHER` | UUID Cartographer в EBB | Cartographer → `[mcu cartographer]` |
| Нет строки / timeout | EBB не на шине | Питание, CAN, прошивка |

#### Шаг 3 — если EBB реально STM32G0 (не RP2040)

В `printer.cfg` закомментируйте **блок A** (gpio*) и раскомментируйте **блок B** (`PA15`, `PD0`…) — extruder, fans, `endstop_pin` X.

#### Шаг 4 — проверка

`FIRMWARE_RESTART` → в логе три строки:

```
MCU 'mcu' config: MCU=stm32f407xx
MCU 'EBBCan' config: MCU=rp2040
MCU 'cartographer' config: … CARTOGRAPHER …
```

| `[mcu cartographer]` | `CARTOGRAPHER` | `stm32f407`, `rp2040` |

### Ошибка `MCU Protocol error` / `Unknown command: tmcuart_send` на EBBCan

Kalico на Pi **не совместим** с прошивкой mainline Klipper на MCU. Плюс UUID могут быть перепутаны.

#### Как читать сообщение об ошибке

Строка `MCU(s) which should be updated` — **какая прошивка сейчас на каком слоте** в `printer.cfg`:

| Слот в printer.cfg | Версия в ошибке | Что это за плата | Куда UUID |
|--------------------|-----------------|------------------|-----------|
| `mcu` | `v0.12.0-…` (Klipper) | Monster8 F407 | UUID Monster8 → `[mcu]` |
| `EBBCan` | `CARTOGRAPHER 5.0.0` | **Cartographer** (перепутан!) | UUID Cartographer → `[mcu cartographer]` |
| `cartographer` | `v0.12.0-…` (Klipper) | **EBB RP2040** (перепутан!) | UUID EBB → `[mcu EBBCan]` |

Пример вашей ошибки — UUID Cartographer и EBB **поменяны местами**:
- в `[mcu EBBCan]` стоит UUID Cartographer → `tmcuart_send` неизвестен (у пробы нет TMC)
- в `[mcu cartographer]` стоит UUID EBB

**Исправление UUID:** верните как было до обмена — EBB UUID в `[mcu EBBCan]`, Cartographer UUID в `[mcu cartographer]`.

#### Прошивки под Kalico

После правки UUID всё равно нужно перепрошить **Monster8** и **EBB** из `~/kalico` (не из `~/klipper`):

| Слот | Нужная прошивка | Откуда |
|------|-----------------|--------|
| `[mcu]` | Kalico, STM32F407 | `~/kalico` (§1) |
| `[mcu EBBCan]` | Kalico, RP2040 CAN | `~/kalico` (§4) |
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
3. UUID с **rp2040** (EBB SB2209) → `[mcu EBBCan]`
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
> PA0 — апп.отсек, PA3 — вытяжка, PA8 — neopixel, nevermore — PA2 (см. `printer.cfg`).

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

## 4. Прошивка EBB по CAN

### Вариант A — EBB SB2209 / SB2040 **RP2040** (пины `gpio*`)

**Kalico menuconfig:**
- MCU: RP2040
- Communication: **CAN bus (gpio4/gpio5)**
- CAN speed: **1000000**
- Bootloader offset: **16KiB** (Katapult)

```bash
sudo systemctl stop klipper
cd ~/kalico && make clean && make
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/katapult/out/katapult.uf2 -u REPLACE_EBB_UUID
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/kalico/out/klipper.uf2 -u REPLACE_EBB_UUID
```

В `printer.cfg` — **блок A** пинов (`gpio18`, `gpio20`, …).

### Вариант B — EBB **STM32G0B1** (пины `PA*` / `PD*` / `PB*`)

На плате чип **STM32G0**, не RP2040. В логе: `MCU 'EBBCan' config: MCU=stm32g0b1xx`.

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

В `printer.cfg` — **блок B** пинов (`PD0`, `PA15`, `PC13` endstop X, …) — **активен по умолчанию** в этом репозитории.

## 5. Прошивка Cartographer

Отдельный репозиторий `~/cartographer_firmware`. См. https://docs.cartographer3d.com

## 6. Терминаторы 120 Ω

- Monster8 (если конец шины)
- EBB SB2209 (джампер 120R)
- Cartographer (если конец шины)

## 7. Проверка

`FIRMWARE_RESTART`, в логе — правильные `MCU=…` для трёх секций, затем `QUERY_ENDSTOPS`, `STATUS`.
