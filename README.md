# Voron 2.4 Gr1mSkull — Klipper конфигурации

Один проект с несколькими готовыми сборками. Каждая сборка — **отдельная папка**
с полным набором конфигов. Выберите нужную и скопируйте её содержимое в
`~/printer_data/config/`.

## Сборки (папки)

| Папка | Сборка | Плата + хост | ОС хоста |
|-------|--------|--------------|----------|
| `klipper_config/` | Voron 2.4 (базовая) | Manta M8P v2.0 + CB2 | BTT CB2 V3.0.2 (Debian 12) |
| `klipper_config_fly_d8/` | Voron 2.4 | FLY-D8 (STM32F407, CAN bridge) + Raspberry Pi 4B | MainsailOS 3.0 |
| `klipper_config_mks_monster8/` | Voron 2.4 | MKS Monster8 V2.0 (STM32F407, CAN bridge) + Raspberry Pi 4B | MainsailOS 3.0 |
| `stealthchanger_config/` | Voron 2.4 + тулченджер (6 голов) | Manta M8P v2.0 + CB2, 6× EBB SB2209 | BTT CB2 V3.0.2 (Debian 12) |

Образы ОС: [BTT CB2 V3.0.2](https://github.com/bigtreetech/CB2/releases/tag/V3.0.2) · [MainsailOS](https://docs.mainsail.xyz/setup/mainsail-os). Оба содержат Klipper + Moonraker + Mainsail из коробки.

Общее для всех сборок: тулхед EBB SB2209 CAN, Clockwork 2 / Stealthburner,
Bambu X1C hotend (Rapido на тулченджере), Voron Tap, опциональный Cartographer,
размер 500×500×480, CAN @ 1000000.

## Как пользоваться

```bash
# развернуть нужную сборку (пример — FLY-D8)
cp -r klipper_config_fly_d8/* ~/printer_data/config/
```

Подробное руководство по сборке и настройке — в `ИНСТРУКЦИЯ.md`
(готовый PDF — `ИНСТРУКЦИЯ.pdf`). В каждой папке конфига есть свой `README.md`
с переключателями (endstops physical/sensorless, привод 2WD/AWD, Cartographer).

## Структура проекта

```
.
├── klipper_config/               # базовая (Manta M8P + CB2)
├── klipper_config_fly_d8/        # FLY-D8 + Raspberry Pi 4B
├── klipper_config_mks_monster8/  # MKS Monster8 V2.0 + Raspberry Pi 4B
├── stealthchanger_config/        # тулченджер, 6 голов
├── images/                       # схемы (mermaid + png)
├── ИНСТРУКЦИЯ.md                 # полное руководство
└── ИНСТРУКЦИЯ.pdf                # то же в PDF (картинки вшиты)
```
