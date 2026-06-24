# CAN bus — Manta M8P v2.0 USB-to-CAN bridge @ 1000000

## 1. Прошивка M8P (Katapult + Klipper bridge)

```bash
sudo systemctl stop klipper
cd ~/klipper
make menuconfig
```

**Katapult (M8P):**
- MCU: STM32H723
- Bootloader: 128KiB
- Clock: 25 MHz
- Communication: **USB to CAN bus bridge**
- CAN: PD0/PD1
- CAN speed: **1000000**

**Klipper (M8P):** те же параметры.

```bash
cd ~/katapult && make clean && make
# DFU: BOOT + RESET
sudo dfu-util -a 0 -D out/katapult.bin --dfuse-address 0x08000000:force:leave -d 0483:df11

cd ~/klipper && make clean && make
sudo dfu-util -a 0 -d 0483:df11 --dfuse-address 0x08020000 -D ~/klipper/out/klipper.bin
```

## 2. Интерфейс can0 на CB2 (образ BTT CB2 V3.0.2 — Debian 12, kernel 6.1)

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

Автозапуск после перезагрузки:

```bash
sudo ln -sf /etc/network/interfaces.d/can0 /etc/network/if-up.d/can0
```

## 3. Прошивка EBB SB2209 CAN (RP2040)

**Katapult:**
- MCU: RP2040
- Communication: **CAN bus (gpio4/gpio5)**
- CAN speed: **1000000**

**Klipper:** те же параметры.

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
- M8P → `[mcu] canbus_uuid`
- EBB → `[mcu EBBCan] canbus_uuid`

## 5. Терминаторы 120 Ω

- Джампер **CAN_120R** на M8P v2.0
- Джампер **120R** на EBB SB2209
- Cartographer на CAN — свой терминатор только если он конец шины

## 6. Проверка

```bash
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer_data/config/printer.cfg -i ~/printer_data/comms/klippy.serial -v
```

В консоли: `FIRMWARE_RESTART`, `QUERY_ENDSTOPS`, `STATUS`
