#!/usr/bin/env python3
"""Assemble monolithic printer.cfg from hardware base + 3Def peripheral modules."""

from pathlib import Path

ROOT = Path(__file__).parent
REF = Path("/tmp/3def")
OUT = ROOT / "printer.cfg"
CURRENT = ROOT / "printer.cfg"

HEADER = """#####################################################################
# Gr1mSkull Voron 2.4 500×500×480 (MKS Monster8 V2.0 + RPi 4B)
#
# Прошивка хоста: Kalico (https://docs.kalico.gg)
# Z-проба: Cartographer 3D | Голова: EBB SB2209 CAN
#
# Единый printer.cfg — периферия по эталону 3Def SB2040V3/500:
#   таймлапс, очистка сопла, StealthBurner LED, датчик филамента,
#   подсветка камеры, Nevermore (без модуля вкл/выкл).
#
# Установка: doc/kalico_setup.md | CAN: doc/can0_setup.md
#####################################################################

"""

# Hardware + Cartographer: lines until STEALTHBURNER LED section (exclusive)
current_lines = CURRENT.read_text(encoding="utf-8").splitlines(keepends=True)
hw_end = next(i for i, line in enumerate(current_lines) if "# STEALTHBURNER LED" in line) - 1
hw_block = "".join(current_lines[:hw_end])

# Heater bed + fans + подсветка (без датчика филамента и homing)
fans_start = next(i for i, line in enumerate(current_lines) if "# НАГРЕВ СТОЛА" in line)
fans_end = next(i for i, line in enumerate(current_lines) if "# ДАТЧИК ФИЛАМЕНТА" in line)
homing_start = next(i for i, line in enumerate(current_lines) if line.startswith("# HOMING") or "# HOMING\n" in line or (line.strip() == "# HOMING"))
# homing header is 3 lines after "ДАТЧИК" block - find [safe_z_home]
homing_start = next(i for i, line in enumerate(current_lines) if line.startswith("[safe_z_home]")) - 6
homing_end = next(i for i, line in enumerate(current_lines) if line.strip() == "max_adjust: 10") + 1
fans_block = "".join(current_lines[fans_start:fans_end])
homing_block = "".join(current_lines[homing_start:homing_end])

FILAMENT = (REF / "filament_sensor.cfg").read_text(encoding="utf-8").replace(
    "pause", "PAUSE"
)

LED = (REF / "led.cfg").read_text(encoding="utf-8")

NEVERMORE_MACROS = """
#####################################################################
# NEVERMORE / ВЫТЯЖКА / ПОДСВЕТКА (эталон 3Def)
#####################################################################

[gcode_macro NEVERMORE_ON]
description: Включить Nevermore
gcode:
    SET_FAN_SPEED FAN=nevermore SPEED=1.0

[gcode_macro NEVERMORE_OFF]
description: Выключить Nevermore
gcode:
    SET_FAN_SPEED FAN=nevermore SPEED=0

[gcode_macro EXHAUST_ON]
description: Включить вытяжку
gcode:
    SET_FAN_SPEED FAN=exhaust_fan SPEED=1.0

[gcode_macro EXHAUST_OFF]
description: Выключить вытяжку
gcode:
    SET_FAN_SPEED FAN=exhaust_fan SPEED=0

[delayed_gcode exhaust_off]
gcode:
    EXHAUST_OFF
    NEVERMORE_OFF

"""

START_END = """
#####################################################################
# СТАРТ / КОНЕЦ / ПАУЗА (эталон 3Def + Cartographer / Orca)
#####################################################################

[gcode_macro _USER_VARIABLES]
variable_probe_max_temp: 150
variable_bed_center_x: 250
variable_bed_center_y: 250
variable_adaptive_margin: 10
gcode:

[gcode_macro CARTO_CALIBRATE]
description: Подсказка по калибровке Cartographer
gcode:
    RESPOND MSG="1) CARTOGRAPHER_SCAN_CALIBRATE → SAVE_CONFIG"
    RESPOND MSG="2) G28 Z → QUAD_GANTRY_LEVEL → G28 Z"
    RESPOND MSG="3) CARTOGRAPHER_TOUCH_CALIBRATE → SAVE_CONFIG"

[gcode_macro G32]
description: G28 + QGL + Z (сопло ≤150°C для Cartographer touch)
gcode:
    {% set probe_temp = printer["gcode_macro _USER_VARIABLES"].probe_max_temp|float %}
    {% set cx = printer["gcode_macro _USER_VARIABLES"].bed_center_x|float %}
    {% set cy = printer["gcode_macro _USER_VARIABLES"].bed_center_y|float %}
    BED_MESH_CLEAR
    status_homing
    G28
    status_heating
    M104 S{probe_temp}
    M109 S{probe_temp}
    status_leveling
    QUAD_GANTRY_LEVEL
    G28 Z
    G0 X{cx} Y{cy} Z30 F3600
    status_ready

[gcode_macro MESH]
description: Ручная сетка; ADAPTIVE=1 — exclude_object; SAVE=1 — SAVE_CONFIG
gcode:
    {% set adaptive = params.ADAPTIVE|default(0)|int %}
    {% set margin = printer["gcode_macro _USER_VARIABLES"].adaptive_margin|int %}
    {% if adaptive %}
        BED_MESH_CALIBRATE ADAPTIVE=1 ADAPTIVE_MARGIN={margin}
    {% else %}
        BED_MESH_CALIBRATE
    {% endif %}
    {% if params.SAVE|default(0)|int %}
        SAVE_CONFIG
    {% endif %}

[gcode_macro PRINT_START]
description: Старт печати (3Def + Orca adaptive mesh + Cartographer touch)
gcode:
    CLEAR_PAUSE
    SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=0
    {% set bedtemp = params.BED_TEMP|default(params.BED|default(60))|int %}
    {% set hotendtemp = params.EXTRUDER_TEMP|default(params.EXTRUDER|default(200))|int %}
    {% set probe_temp = printer["gcode_macro _USER_VARIABLES"].probe_max_temp|float %}
    onled
    status_ready
    BED_MESH_CLEAR
    status_homing
    G28
    G90
    status_heating
    M104 S{probe_temp}
    M140 S{bedtemp}
    M190 S{bedtemp}
    M109 S{probe_temp}
    status_leveling
    QUAD_GANTRY_LEVEL
    G28 Z
    status_calibrating_z
    CARTOGRAPHER_TOUCH_HOME
    status_meshing
    {% if params.MESH_MIN_X is defined %}
        BED_MESH_CALIBRATE mesh_min={params.MESH_MIN_X|float},{params.MESH_MIN_Y|float} mesh_max={params.MESH_MAX_X|float},{params.MESH_MAX_Y|float} ALGORITHM={params.MESH_ALGO|default("bicubic")} PROBE_COUNT={params.PROBE_COUNT_X|int},{params.PROBE_COUNT_Y|int} ADAPTIVE=0 ADAPTIVE_MARGIN=0
    {% else %}
        BED_MESH_CALIBRATE
    {% endif %}
    M104 S{hotendtemp}
    M109 S{hotendtemp}
    status_cleaning
    clean_nozzle
    status_printing
    G92 E0
    G1 X5 Y3 F5000
    G1 Z0.32 F400
    G1 X450 Y3 E38 F3000
    G1 Z0.5 F200
    G92 E0
    SET_PIN PIN=beeper VALUE=1
    G4 P3000
    SET_PIN PIN=beeper VALUE=0
    SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=1

[gcode_macro PRINT_END]
description: Конец печати (3Def, без автоотключения питания)
gcode:
    M400
    G92 E0
    G91
    G0 Z1.00 X20.0 Y20.0 F6000
    TURN_OFF_HEATERS
    M107
    G1 Z2 F3000
    G90
    G0 X495 Y495 F3600
    BED_MESH_CLEAR
    NEVERMORE_ON
    EXHAUST_ON
    UPDATE_DELAYED_GCODE ID=exhaust_off DURATION=600
    SET_PIN PIN=beeper VALUE=1
    G4 P3000
    SET_PIN PIN=beeper VALUE=0
    G4 P3000
    SET_PIN PIN=beeper VALUE=1
    G4 P3000
    SET_PIN PIN=beeper VALUE=0

[gcode_macro _TOOLHEAD_PARK_PAUSE_CANCEL]
description: Парковка при PAUSE / CANCEL_PRINT
variable_extrude: 1.0
gcode:
    {% set x_park = printer.toolhead.axis_maximum.x|float - 5.0 %}
    {% set y_park = printer.toolhead.axis_maximum.y|float - 5.0 %}
    {% set z_park_delta = 2.0 %}
    {% set max_z = printer.toolhead.axis_maximum.z|float %}
    {% set act_z = printer.toolhead.position.z|float %}
    {% if act_z < (max_z - z_park_delta) %}
        {% set z_safe = z_park_delta %}
    {% else %}
        {% set z_safe = max_z - act_z %}
    {% endif %}
    {% if printer.extruder.can_extrude|lower == 'true' %}
        M83
        G1 E-{extrude} F2100
        {% if printer.gcode_move.absolute_extrude |lower == 'true' %} M82 {% endif %}
    {% else %}
        {action_respond_info("Extruder not hot enough")}
    {% endif %}
    {% if "xyz" in printer.toolhead.homed_axes %}
        G91
        G1 Z{z_safe} F900
        G90
        G1 X{x_park} Y{y_park} F6000
        {% if printer.gcode_move.absolute_coordinates|lower == 'false' %} G91 {% endif %}
    {% else %}
        {action_respond_info("Printer not homed")}
    {% endif %}

[gcode_macro PAUSE]
description: Пауза печати
rename_existing: BASE_PAUSE
gcode:
    BASE_PAUSE
    _TOOLHEAD_PARK_PAUSE_CANCEL

[gcode_macro RESUME]
description: Продолжить печать
rename_existing: BASE_RESUME
gcode:
    {% set extrude = printer['gcode_macro _TOOLHEAD_PARK_PAUSE_CANCEL'].extrude %}
    {% if 'VELOCITY' in params|upper %}
        {% set get_params = ('VELOCITY=' + params.VELOCITY) %}
    {% else %}
        {% set get_params = "" %}
    {% endif %}
    {% if printer.extruder.can_extrude|lower == 'true' %}
        M83
        G1 E{extrude} F2100
        {% if printer.gcode_move.absolute_extrude |lower == 'true' %} M82 {% endif %}
    {% else %}
        {action_respond_info("Extruder not hot enough")}
    {% endif %}
    BASE_RESUME {get_params}

[gcode_macro CANCEL_PRINT]
description: Отмена печати
rename_existing: BASE_CANCEL_PRINT
variable_park: True
gcode:
    {% if printer.pause_resume.is_paused|lower == 'false' and park|lower == 'true' %}
        _TOOLHEAD_PARK_PAUSE_CANCEL
    {% endif %}
    TURN_OFF_HEATERS
    BASE_CANCEL_PRINT

[gcode_macro LOAD_FILAMENT]
variable_load_distance: 100
variable_purge_distance: 25
gcode:
    {% set speed = params.SPEED|default(300) %}
    {% set max_velocity = printer.configfile.settings['extruder'].max_extrude_only_velocity * 60 %}
    SAVE_GCODE_STATE NAME=load_state
    SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=0
    G91
    G92 E0
    G1 E{load_distance} F{max_velocity}
    G1 E{purge_distance} F{speed}
    SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=0
    RESTORE_GCODE_STATE NAME=load_state

[gcode_macro UNLOAD_FILAMENT]
variable_unload_distance: 100
variable_purge_distance: 25
gcode:
    {% set speed = params.SPEED|default(300) %}
    {% set max_velocity = printer.configfile.settings['extruder'].max_extrude_only_velocity * 60 %}
    SAVE_GCODE_STATE NAME=unload_state
    G91
    G92 E0
    G1 E{purge_distance} F{speed}
    G1 E-{unload_distance} F{max_velocity}
    RESTORE_GCODE_STATE NAME=unload_state

[gcode_macro SGTHRS_TEST]
description: Тест sensorless — SGTHRS_TEST AXIS=X VALUE=80
gcode:
    {% set axis = params.AXIS|default('X')|upper %}
    {% set val = params.VALUE|default(80)|int %}
    {% if axis == 'X' %}
        SET_TMC_FIELD STEPPER=stepper_x FIELD=SGTHRS VALUE={val}
    {% elif axis == 'Y' %}
        SET_TMC_FIELD STEPPER=stepper_y FIELD=SGTHRS VALUE={val}
    {% else %}
        { action_raise_error("AXIS must be X or Y") }
    {% endif %}
    M117 {axis} SGTHRS={val}
    G28 {axis}

"""


def strip_stealthburner_leds(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    skip_neopixel = False
    for line in lines:
        if line.strip().startswith("[neopixel sb_leds]"):
            skip_neopixel = True
            continue
        if skip_neopixel:
            if line.startswith("[") and not line.startswith("[neopixel"):
                skip_neopixel = False
            else:
                continue
        if line.strip().startswith("#MACROS") or line.strip() == "#开启三维科技":
            continue
        out.append(line)
    return "".join(out)


def strip_nozzle_header(text: str) -> str:
    lines = text.splitlines(keepends=True)
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "[gcode_macro clean_nozzle]":
            start = i
            break
    return (
        "#####################################################################\n"
        "# ОЧИСТКА СОПЛА (эталон 3Def nozzle_scrub.cfg)\n"
        "#####################################################################\n\n"
        + "".join(lines[start:])
    )


def extract_save_config(text: str) -> str:
    for i, line in enumerate(text.splitlines(keepends=True)):
        if "#*# <---------------------- SAVE_CONFIG" in line:
            return (
                "\n# KlipperScreen: ~/KlipperScreen/KlipperScreen.conf\n\n"
                + "".join(text.splitlines(keepends=True)[i:])
            )
    return ""


def main() -> None:
    nozzle = strip_nozzle_header((REF / "nozzle_scrub.cfg").read_text(encoding="utf-8"))
    sb_leds = strip_stealthburner_leds(
        (REF / "stealthburner_leds.cfg").read_text(encoding="utf-8")
    )
    # Fix pin reference for EBB (3def uses sb2040:gpio26 — hardware already has neopixel)
    timelapse = (REF / "timelapse.cfg").read_text(encoding="utf-8")
    save_config = extract_save_config(CURRENT.read_text(encoding="utf-8"))

    # Fix LOAD_FILAMENT typo: ENABLE=1 on restore
    start_end = START_END.replace(
        "SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=0\n    RESTORE_GCODE_STATE NAME=load_state",
        "SET_FILAMENT_SENSOR SENSOR=Пластик ENABLE=1\n    RESTORE_GCODE_STATE NAME=load_state",
    )

    parts = [
        HEADER,
        hw_block,
        fans_block,
        homing_block,
        "\n#####################################################################\n",
        "# ДАТЧИК ФИЛАМЕНТА (эталон 3Def)\n",
        "#####################################################################\n\n",
        FILAMENT,
        NEVERMORE_MACROS,
        LED,
        "\n#####################################################################\n",
        "# STEALTHBURNER LED (эталон 3Def)\n",
        "#####################################################################\n\n",
        sb_leds,
        "[delayed_gcode set_stealthburner_led]\n",
        "initial_duration: 2\n",
        "gcode:\n",
        "    status_ready\n\n",
        start_end,
        nozzle,
        "\n#####################################################################\n",
        "# ТАЙМЛАПС (moonraker-timelapse, эталон 3Def)\n",
        "#####################################################################\n\n",
        timelapse,
        save_config,
    ]
    content = "".join(parts)
  # sanity: forbidden tokens
    forbidden = ["shut_down", "SHUT_DOWN", "offmodule", "DWGJ", "powerOFF", "[include"]
    for token in forbidden:
        if token.lower() in content.lower() and token != "[include":
            raise SystemExit(f"Forbidden token found: {token}")
        if token == "[include" and "[include" in content:
            raise SystemExit("Forbidden [include] found")
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    main()
