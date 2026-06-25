# CAN bus — FLY-D8 USB-to-CAN bridge @ 1000000 + Raspberry Pi 4B (MainsailOS 3.0)

> RPi 4B не имеет CAN-контроллера. Мост (bridge) поднимает плата FLY-D8:
> по USB она выглядит для RPi как CAN-адаптер, и EBB SB2209 виден на той же шине.

## 1. Прошивка FLY-D8 (Katapult + Klipper bridge)

```bash
sudo systemctl stop klipper
cd ~/klipper
make menuconfig
```

**Katapult (FLY-D8):**
- MCU: STM32F407
- Bootloader offset: **32KiB**
- Clock: 8/25 MHz (по плате) — см. документацию FLY
- Communication: **USB to CAN bus bridge (USB on PA11/PA12)**
- CAN bus: пины согласно документации FLY-D8 (для STM32F407 обычно PD0/PD1 или PB8/PB9 — **проверьте**)
- CAN speed: **1000000**

**Klipper (FLY-D8):** те же параметры.

```bash
cd ~/katapult && make clean && make
# Режим DFU: двойное нажатие RST (Type-C подключён)
sudo dfu-util -a 0 -D out/katapult.bin --dfuse-address 0x08000000:force:leave -d 0483:df11

cd ~/klipper && make clean && make
sudo dfu-util -a 0 -d 0483:df11 --dfuse-address 0x08008000 -D ~/klipper/out/klipper.bin
```

> ⚠ Адрес Klipper = 0x08000000 + размер bootloader. Для 32KiB → 0x08008000.

## 2. Интерфейс can0 на Raspberry Pi 4B (MainsailOS 3.0)

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

## 3. Прошивка EBB SB2209 CAN (RP2040)

**Katapult / Klipper:**
- MCU: RP2040
- Communication: **CAN bus (gpio4/gpio5)**
- CAN speed: **1000000**

Прошивка через CAN после настройки can0:

```bash
sudo systemctl stop klipper
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/katapult/out/katapult.uf2 -u REPLACE_EBB_UUID
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/klipper/out/klipper.uf2 -u REPLACE_EBB_UUID
```

## 4. Получение UUID

```bash
sudo systemctl stop klipper
python3 ~/katapult/scripts/flash_can.py -q
sudo systemctl start klipper
```

Запишите UUID в `mcu.cfg`:
- FLY-D8 (bridge) → `[mcu] canbus_uuid`
- EBB → `[mcu EBBCan] canbus_uuid`

## 5. Терминаторы 120 Ω

- Джампер CAN 120R на FLY-D8 (если плата — конец шины)
- Джампер 120R на EBB SB2209
- Cartographer на CAN — свой терминатор только если он конец шины

## 6. Проверка

В консоли Klipper: `FIRMWARE_RESTART`, `QUERY_ENDSTOPS`, `STATUS`
