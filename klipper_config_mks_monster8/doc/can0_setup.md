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

Пины `gpio18`, `gpio20`… работают только на **EBB SB2209 RP2040**.

1. В логе смотрите `MCU 'EBBCan' config: MCU=…`
2. Если **`stm32g0b1`** — UUID перепутан (часто попадает UTOC вместо EBB). Исправьте UUID.
3. Если **`rp2040`**, но gpio не принимаются — перепрошейте EBB из `~/kalico` (RP2040, CAN gpio4/5 @ 1M).
4. Если плата **STM32G0** (не RP2040) — в `printer.cfg` блок B пинов (`PA15`, `PD0`…).

| `[mcu cartographer]` | `CARTOGRAPHER` | `stm32f407`, `rp2040` |

### Типичная ошибка (как в вашем логе)

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

## 4. Прошивка EBB SB2209 CAN (RP2040)

**Katapult / Kalico:**
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

## 5. Прошивка Cartographer

Отдельный репозиторий `~/cartographer_firmware`. См. https://docs.cartographer3d.com

## 6. Терминаторы 120 Ω

- Monster8 (если конец шины)
- EBB SB2209 (джампер 120R)
- Cartographer (если конец шины)

## 7. Проверка

`FIRMWARE_RESTART`, в логе — правильные `MCU=…` для трёх секций, затем `QUERY_ENDSTOPS`, `STATUS`.
