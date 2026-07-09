# CAN bus — MKS Monster8 V2.0 + RPi 4B (Kalico @ 1000000)

> Прошивки MCU собирайте из **~/kalico**, не из ~/klipper.
> Установка Kalico и плагина Cartographer: `doc/kalico_setup.md`

## 1. Прошивка Monster8 (Katapult + Kalico CAN bridge)

> **Рекомендуемый способ** — Katapult через DFU. Полная пошаговая инструкция (в т.ч. восстановление после неудачной SD-прошивки): **`doc/katapult_flash_from_scratch.md`**

### 1.1 Katapult (bootloader, один раз)

```bash
sudo systemctl stop klipper
cd ~/katapult
make menuconfig
```

**Katapult:**
- MCU: **STM32F407**
- Build Katapult deployment application: **Do not build**
- Clock: **8 MHz crystal**
- Communication: **USB (on PA11/PA12)** — не CAN!
- Application start offset: **32KiB**
- [*] Support bootloader entry on rapid double click of reset button

```bash
cd ~/katapult && make clean && make
```

**DFU:** зажать BOOT0 → RESET → отпустить RESET → счёт до 5 → отпустить BOOT0.

```bash
lsusb | grep -i dfu   # STM Device in DFU mode
sudo dfu-util -R -a 0 -s 0x08000000:mass-erase:force:leave -D ~/katapult/out/katapult.bin -d 0483:df11
```

Проверка: **дважды RESET** → `ls /dev/serial/by-id/ | grep katapult`

### 1.2 Kalico (USB-to-CAN bridge)

```bash
cd ~/kalico
make menuconfig
```

**Kalico (Monster8 V2.0):**
- MCU: **STM32F407**
- Bootloader offset: **32KiB**
- Clock: **8 MHz crystal**
- Communication: **USB to CAN bus bridge (USB on PA11/PA12)**
- CAN bus interface: **CAN bus (on PB12/PB13)**
- CAN speed: **1000000**

```bash
cd ~/kalico && make clean && make
KATAPULT_DEV=$(ls /dev/serial/by-id/usb-katapult_* | head -1)
python3 ~/katapult/scripts/flashtool.py -d "$KATAPULT_DEV" -f ~/kalico/out/klipper.bin
```

### 1.3 Альтернатива: stock bootloader MKS (microSD)

Если Katapult не нужен и работает штатный загрузчик MKS (48 KiB):

- Bootloader offset: **48KiB**
- Прошивка: `out/klipper.bin` → microSD как **`mks_monster8.bin`** → перезагрузка

> После неудачной SD-прошивки используйте Katapult (раздел 1.1) — DFU работает независимо от состояния прошивки.

---

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

---

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

---

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

---

## 5. Прошивка Cartographer

Отдельный репозиторий `~/cartographer_firmware`. См. https://docs.cartographer3d.com

---

## 6. Терминаторы 120 Ω

- Monster8 — **постоянный 120 Ω на плате** (отключить нельзя)
- EBB SB2209 (джампер 120R)
- Cartographer (если конец шины)

---

## 7. Проверка

`FIRMWARE_RESTART`, `QUERY_ENDSTOPS`, `STATUS`
