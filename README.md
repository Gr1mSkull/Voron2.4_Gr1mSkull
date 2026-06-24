# Voron 2.4 Gr1mSkull — Klipper конфигурации

Репозиторий с несколькими сборками. Каждая сборка вынесена в **отдельную
git-ветку**. Переключайтесь между ними через `git checkout <branch>`.

## Ветки

| Ветка | Сборка | Плата + хост | ОС хоста | Папка конфига |
|-------|--------|--------------|----------|----------------|
| `main` | Voron 2.4 (базовая) | Manta M8P v2.0 + CB2 | BTT CB2 V3.0.2 (Debian 12) | `klipper_config/` |
| `fly-d8` | Voron 2.4 | FLY-D8 (STM32F407, CAN bridge) + Raspberry Pi 4B | MainsailOS 3.0 | `klipper_config_fly_d8/` |
| `mks-monster8` | Voron 2.4 | MKS Monster8 V2.0 (STM32F407, CAN bridge) + Raspberry Pi 4B | MainsailOS 3.0 | `klipper_config_mks_monster8/` |
| `stealthchanger` | Voron 2.4 + тулченджер | Manta M8P v2.0 + CB2, 6× EBB SB2209 | BTT CB2 V3.0.2 (Debian 12) | `stealthchanger_config/` |

Образы ОС: [BTT CB2 V3.0.2](https://github.com/bigtreetech/CB2/releases/tag/V3.0.2) · [MainsailOS](https://docs.mainsail.xyz/setup/mainsail-os). Оба содержат Klipper + Moonraker + Mainsail из коробки.

Общее для всех веток: тулхед EBB SB2209 CAN, Clockwork 2 / Stealthburner,
Bambu X1C hotend (Rapido на тулченджере), Voron Tap, опциональный Cartographer,
размер 500×500×480, CAN @ 1000000.

## Как пользоваться

```bash
# посмотреть список веток
git branch -a

# выбрать сборку
git checkout fly-d8

# развернуть конфиг (имя папки зависит от ветки — см. таблицу выше)
cp -r klipper_config_fly_d8/* ~/printer_data/config/
```

Подробное руководство по сборке и настройке — в `ИНСТРУКЦИЯ.md`
(присутствует во всех ветках). В каждой папке конфига есть свой `README.md`
с переключателями (endstops physical/sensorless, привод 2WD/AWD, Cartographer).
