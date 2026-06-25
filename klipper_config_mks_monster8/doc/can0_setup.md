# CAN bus — MKS Monster8 V2.0 USB-to-CAN bridge @ 1000000 + Raspberry Pi 4B (MainsailOS 3.0)

> RPi 4B не имеет CAN-контроллера. Мост (bridge) поднимает плата Monster8 V2.0
> (встроенный CAN-трансивер): по USB она выглядит для RPi как CAN-адаптер,
> и EBB SB2209 виден на той же шине.

## 1. Прошивка Monster8 (Klipper в режиме bridge)

```bash
sudo systemctl stop klipper
cd ~/klipper
make menuconfig
```

**Klipper (Monster8 V2.0):**
- MCU: STM32F407
- Bootloader offset: **48KiB**
- Clock: 8 MHz crystal
- Communication: **USB to CAN bus bridge (USB on PA11/PA12)**
- CAN bus: пины согласно документации Monster8 V2.0 (для STM32F407 обычно PD0/PD1 или PB8/PB9 — **проверьте**)
- CAN speed: **1000000**

Прошивка Monster8 выполняется через SD/U-диск (DFU тоже доступен):

```bash
cd ~/klipper && make clean && make
# Скопируйте out/klipper.bin на microSD как mks_monster8.bin,
# вставьте карту и перезагрузите плату (файл перезапишется в *.CUR).
```

> ⚠ Имя файла должно быть строго `mks_monster8.bin`. Если плата уже
> прошита, при следующем обновлении используйте новое имя или удалите
> старый `*.CUR` с карты.

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
- Monster8 (bridge) → `[mcu] canbus_uuid`
- EBB → `[mcu EBBCan] canbus_uuid`

## 5. Терминаторы 120 Ω

- Терминатор CAN на Monster8 V2.0 (джампер/резистор, если плата — конец шины)
- Джампер 120R на EBB SB2209
- Cartographer на CAN — свой терминатор только если он конец шины

## 6. Проверка

В консоли Klipper: `FIRMWARE_RESTART`, `QUERY_ENDSTOPS`, `STATUS`
