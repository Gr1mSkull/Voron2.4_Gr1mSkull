# CAN bus — MKS Monster8 V2.0 + RPi 4B (Kalico @ 1000000)

> Прошивки MCU собирайте из **~/kalico**, не из ~/klipper.
> Установка Kalico и плагина Cartographer: `doc/kalico_setup.md`

## 1. Прошивка Monster8 (Kalico, режим USB-to-CAN bridge)

```bash
sudo systemctl stop klipper
cd ~/kalico
make menuconfig
```

**Kalico (Monster8 V2.0):**
- MCU: STM32F407
- Bootloader offset: **48KiB**
- Clock: 8 MHz crystal
- Communication: **USB to CAN bus bridge (USB on PA11/PA12)**
- CAN speed: **1000000**

```bash
cd ~/kalico && make clean && make
# out/klipper.bin → microSD как mks_monster8.bin → перезагрузка платы
```

## 2. Интерфейс can0 (MainsailOS)

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

## 4. Получение UUID

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
```

| UUID → секция | Устройство |
|---------------|------------|
| `[mcu]` | MKS Monster8 |
| `[mcu EBBCan]` | EBB SB2209 (голова) |
| `[mcu cartographer]` | Cartographer |

**Проверка после `FIRMWARE_RESTART`:**

| Секция | Версия прошивки |
|--------|-----------------|
| `mcu` | Kalico (та же, что хост) |
| `EBBCan` | Kalico |
| `cartographer` | `CARTOGRAPHER x.x.x` |

Если `EBBCan` показывает `CARTOGRAPHER` — UUID перепутан с пробой.

## 5. Прошивка Cartographer

Отдельный репозиторий `~/cartographer_firmware`. См. https://docs.cartographer3d.com

## 6. Терминаторы 120 Ω

- Monster8 (если конец шины)
- EBB SB2209 (джампер 120R)
- Cartographer (если конец шины)

## 7. Проверка

`FIRMWARE_RESTART`, `QUERY_ENDSTOPS`, `STATUS`
