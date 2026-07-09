# MKS Monster8 V2.0 — прошивка с нуля через Katapult

> Используйте эту инструкцию, если обновление через microSD (`mks_monster8.bin`) не удалось
> или вы хотите перейти на Katapult для последующих обновлений по USB/CAN.

Прошивки собирайте из **~/kalico**, Katapult — из **~/katapult**.

---

## 0. Безопасность и подготовка платы

1. **Отключите нагреватели** (стол, сопло) от разъёмов HE — в DFU-режиме пины могут случайно включить нагрев.
2. **24V на плату пока не подавайте** — для первых шагов достаточно USB от Raspberry Pi.
3. На Monster8 V2.0:
   - **USB power jumper** — установлен (питание MCU от USB).
   - **SELECT jumpers (CAN)** — на **LEFT + MIDDLE** (штатный CAN-трансивер).
   - Плата подключена к RPi по **USB-C**.
4. На плате **постоянный терминатор 120 Ω** — отдельный джампер не нужен.

---

## 1. Подготовка Raspberry Pi (SSH)

```bash
sudo systemctl stop klipper
sudo apt update
sudo apt install -y dfu-util git python3-serial
```

Katapult (если ещё нет):

```bash
cd ~
[ ! -d katapult ] && git clone https://github.com/Arksine/katapult.git
```

Kalico (если ещё нет):

```bash
cd ~
[ ! -d kalico ] && git clone https://github.com/KalicoCrew/kalico.git
```

---

## 2. Сборка и прошивка Katapult (bootloader)

```bash
cd ~/katapult
make menuconfig
```

**Katapult — настройки menuconfig:**

| Параметр | Значение |
|----------|----------|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | **STM32F407** |
| Build Katapult deployment application | **Do not build** |
| Clock Reference | **8 MHz crystal** |
| Communication interface | **USB (on PA11/PA12)** ← не CAN! |
| Application start offset | **32KiB offset** |
| Support bootloader entry on rapid double click of reset button | **[*] включить** |

> Важно: для самого Katapult выбирается **USB**, не CAN. CAN понадобится только в прошивке Kalico (шаг 4).

```bash
cd ~/katapult
make clean && make
```

### Вход в DFU-режим

1. Зажать **BOOT0**.
2. Нажать и отпустить **RESET** (BOOT0 всё ещё зажат).
3. Сосчитать до 5, отпустить **BOOT0**.

Проверка:

```bash
lsusb | grep -i dfu
# Ожидается: STMicroelectronics STM Device in DFU mode
```

### Прошивка Katapult

```bash
sudo dfu-util -R -a 0 -s 0x08000000:mass-erase:force:leave -D ~/katapult/out/katapult.bin -d 0483:df11
```

Достаточно строки **`File downloaded successfully`**. Ошибка на последней строке часто не критична.

Если `mass-erase` не проходит, попробуйте без него:

```bash
sudo dfu-util -R -a 0 -D ~/katapult/out/katapult.bin --dfuse-address 0x08000000:force:leave -d 0483:df11
```

### Проверка Katapult

**Дважды быстро** нажмите **RESET**:

```bash
lsusb | grep -i katapult
ls /dev/serial/by-id/ | grep -i katapult
```

Должно появиться устройство вида `usb-katapult_stm32f407xx_...`.

---

## 3. Сборка Kalico (USB-to-CAN bridge)

```bash
cd ~/kalico
make menuconfig
```

**Kalico — настройки menuconfig:**

| Параметр | Значение |
|----------|----------|
| Enable extra low-level configuration options | **[*] включить** |
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | **STM32F407** |
| Bootloader offset | **32KiB bootloader** |
| Clock Reference | **8 MHz crystal** |
| Communication interface | **USB to CAN bus bridge (USB on PA11/PA12)** |
| CAN bus interface | **CAN bus (on PB12/PB13)** |
| CAN bus speed | **1000000** |

> CAN-интерфейс должен соответствовать джамперам SELECT (LEFT+MIDDLE). Если CAN не поднимется — сверьтесь с [PIN.pdf MKS Monster8 V2.0](https://github.com/makerbase-mks/MKS-Monster8/blob/main/hardware/MKS%20Monster8%20V2.0_003/MKS%20Monster8%20V2.0_003%20PIN.pdf).

```bash
cd ~/kalico
make clean && make
```

---

## 4. Прошивка Kalico через Katapult (USB)

Плата должна быть в режиме Katapult (двойной RESET, см. шаг 2).

```bash
KATAPULT_DEV=$(ls /dev/serial/by-id/usb-katapult_* 2>/dev/null | head -1)
echo "Katapult device: $KATAPULT_DEV"

python3 ~/katapult/scripts/flashtool.py \
  -d "$KATAPULT_DEV" \
  -f ~/kalico/out/klipper.bin
```

Альтернатива (старый синтаксис, тот же скрипт):

```bash
python3 ~/katapult/scripts/flash_can.py -d "$KATAPULT_DEV" -f ~/kalico/out/klipper.bin
```

После успешной прошивки плата перезагрузится. В `lsusb` появится **USB CAN adapter** (не serial-устройство Klipper).

---

## 5. Интерфейс can0

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

Теперь можно подать **24V** на плату (нагреватели пока отключены).

---

## 6. UUID и проверка

```bash
sudo systemctl stop klipper
~/klippy-env/bin/python ~/kalico/scripts/canbus_query.py can0
```

Запишите UUID в `mcu.cfg`:

```ini
[mcu]
canbus_uuid: <UUID Monster8>
canbus_interface: can0
```

```bash
sudo systemctl start klipper
```

В консоли Mainsail: `FIRMWARE_RESTART`, затем `STATUS`.

---

## 7. EBB SB2209 (если нужно прошить заново)

См. `doc/can0_setup.md`, раздел «Прошивка EBB SB2209 CAN».

Кратко:

```bash
sudo systemctl stop klipper
# Katapult для EBB — RP2040, CAN gpio4/gpio5, offset 16KiB
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/katapult/out/katapult.uf2 -u <EBB_UUID>
python3 ~/katapult/scripts/flash_can.py -i can0 -f ~/kalico/out/klipper.uf2 -u <EBB_UUID>
```

---

## Обновления в будущем

| Что обновляем | Как |
|---------------|-----|
| Kalico на Monster8 | `make clean && make` в ~/kalico → `flashtool.py -d <katapult_dev> -f ~/kalico/out/klipper.bin` (двойной RESET если Katapult не виден) |
| Kalico на EBB | `flash_can.py -i can0 -f ~/kalico/out/klipper.uf2 -u <EBB_UUID>` |
| Katapult на Monster8 | Обычно не нужно; при необходимости — снова DFU (шаг 2) |

---

## Альтернатива: Katapult Deployer через microSD

Если DFU недоступен, но **штатный загрузчик MKS (48 KiB) ещё жив**:

1. В Katapult menuconfig: **Build Katapult deployment application → 48KiB bootloader**.
2. `make clean && make` → появится `out/deployer.bin`.
3. Скопировать на microSD как **`mks_monster8.bin`**, перезагрузить плату.
4. Deployer заменит stock bootloader на Katapult и перезагрузится.
5. Дальше — шаги 3–6 этой инструкции (Kalico с **32KiB** offset).

---

## Устранение неполадок

| Симптом | Решение |
|---------|---------|
| `lsusb` не показывает DFU | Проверьте USB-C кабель (data, не charge-only), другой порт RPi; повторите BOOT0+RESET |
| Katapult не виден после DFU | Дважды RESET; проверьте `ls /dev/serial/by-id/` |
| `can0` не поднимается | `sudo ifup can0`; проверьте SELECT jumpers LEFT+MIDDLE |
| `canbus_query.py` пустой | Подайте 24V; на шине нужен хотя бы один CAN-узел (EBB/Cartographer) + терминаторы |
| Неверный offset после SD | Перешейте Katapult через DFU с `mass-erase` — это сотрёт битую прошивку |
| Нагрев в DFU | Отключите HE-разъёмы перед DFU |
