import copy

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.light import ColorMode
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)

# AiotDevice Mapping
MK_MAPPING_PARAMS = "mapping_params"
MK_INIT_PARAMS = "init_params"
MK_RESOURCES = "resources"
MK_HASS_NAME = "hass_attr_name"

# ======================== Reusable sensor fragments ========================

SENSOR_POWER = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "power",
        "device_class": BinarySensorDeviceClass.POWER,
        "state_class": "measurement",
        "unit_of_measurement": UnitOfPower.WATT,
    },
    MK_RESOURCES: {"power": ("0.12.85", "_attr_native_value")},
}}

SENSOR_ENERGY = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "energy",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": "total_increasing",
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
    },
    MK_RESOURCES: {"energy": ("0.13.85", "_attr_native_value")},
}}

SENSOR_BATTERY = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "battery",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": "measurement",
        "unit_of_measurement": PERCENTAGE,
    },
    MK_RESOURCES: {"battery": ("8.0.2001", "_attr_native_value")},
}}

SENSOR_TEMPERATURE = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": "measurement",
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
    },
    MK_RESOURCES: {"temperature": ("0.1.85", "_attr_native_value")},
}}

SENSOR_HUMIDITY = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": "measurement",
        "unit_of_measurement": PERCENTAGE,
    },
    MK_RESOURCES: {"humidity": ("0.2.85", "_attr_native_value")},
}}

SENSOR_PRESSURE = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "pressure",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "state_class": "measurement",
        "unit_of_measurement": UnitOfPressure.HPA,
    },
    MK_RESOURCES: {"pressure": ("0.3.85", "_attr_native_value")},
}}

SENSOR_ILLUMINANCE = {"sensor": {
    MK_INIT_PARAMS: {
        MK_HASS_NAME: "illuminance",
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "state_class": "measurement",
        "unit_of_measurement": LIGHT_LUX,
    },
    MK_RESOURCES: {"illumination": ("0.3.85", "_attr_native_value")},
}}

# ======================== Params templates ========================

PARAMS_TEMPLATES = {
    # ---- Gateways ----
    "gateway_m1s": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.HS,
                "supported_color_modes": [ColorMode.BRIGHTNESS, ColorMode.HS],
            },
            MK_RESOURCES: {
                "toggle": ("14.7.111", "_attr_is_on"),
                "color": ("14.7.85", "_attr_hs_color"),
                "brightness": ("14.7.1006", "_attr_brightness"),
            },
        }},
        SENSOR_ILLUMINANCE,
    ],
    "gateway_no_params": [],

    # ---- Wall switches (single key) ----
    "switch_1_neutral": [
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "wall_switch"},
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
        SENSOR_POWER, SENSOR_ENERGY,
    ],
    "switch_1_no_neutral": [
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "wall_switch"},
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],

    # ---- Wall switches (multi key, requires ch_count override) ----
    "switch_multi_neutral": [
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "wall_switch"},
            MK_RESOURCES: {
                "toggle": ("4.{}.85", "_attr_is_on"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
        SENSOR_POWER, SENSOR_ENERGY,
    ],
    "switch_multi_no_neutral": [
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "wall_switch"},
            MK_RESOURCES: {
                "toggle": ("4.{}.85", "_attr_is_on"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],

    # ---- Plugs / Outlets / Control modules ----
    "plug_with_power": [
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "switch"},
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "power": ("0.12.85", "_attr_current_power_w"),
                "energy": ("0.13.85", "_attr_today_energy_kwh"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
        SENSOR_POWER, SENSOR_ENERGY,
    ],

    # ---- Lights ----
    "light_cct_14x": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.XY,
                "supported_color_mode": [ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP],
                "min_color_temp_kelvin": 2703,
                "max_color_temp_kelvin": 6536,
            },
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "brightness": ("14.1.85", "_attr_brightness"),
                "color_temp": ("14.2.85", "_attr_color_temp_kelvin"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],
    "light_cct_1x": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.XY,
                "supported_color_mode": [ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP],
            },
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "brightness": ("1.7.85", "_attr_brightness"),
                "color_temp": ("1.9.85", "_attr_color_temp_kelvin"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],
    "light_rgb": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.HS,
                "supported_color_mode": [ColorMode.BRIGHTNESS, ColorMode.HS],
            },
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "brightness": ("14.1.85", "_attr_brightness"),
                "color_temp": ("14.2.85", "_attr_color_temp_kelvin"),
                "color": ("14.8.85", "_attr_hs_color"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],
    "light_rgbw_dimmer": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.XY,
                "supported_color_mode": [ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP],
                "min_color_temp_kelvin": 2703,
                "max_color_temp_kelvin": 6536,
            },
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "brightness": ("14.1.85", "_attr_brightness"),
                "color_temp": ("14.2.85", "_attr_color_temp_kelvin"),
                "color": ("14.8.85", "_attr_hs_color"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
        SENSOR_ENERGY,
    ],

    # ---- Wireless buttons ----
    "button_single": [
        {"button": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "action",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"button": ("13.1.85", "_attr_press_type")},
        }},
    ],
    "button_multi": [
        {"button": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "action",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"button": ("13.{}.85", "_attr_press_type")},
        }},
    ],
    "button_rotary": [
        {"button": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "action",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"button": ("13.1.85", "_attr_press_type")},
        }},
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "rotation_angle",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"state": ("0.22.85", "_attr_native_value")},
        }},
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "press_rotation_angle",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"state": ("0.29.85", "_attr_native_value")},
        }},
    ],

    # ---- Sensors ----
    "sensor_th": [SENSOR_TEMPERATURE, SENSOR_HUMIDITY],
    "sensor_th_pressure": [SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_PRESSURE],
    "sensor_motion": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "motion",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "motion": ("3.1.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
    ],
    "sensor_motion_lux": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "motion",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "motion": ("3.1.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
        SENSOR_ILLUMINANCE,
    ],
    "sensor_motion_precision": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "motion",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "motion": ("3.1.85", "_attr_native_value"),
                "detect_time": ("8.0.2115", "_attr_detect_time"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
    ],
    "sensor_presence_fp1": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "exist",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "exist": ("4.1.85", "_attr_native_value"),
                "monitor_type": ("3.51.85", "_attr_monitor_type"),
                "direction_status": ("13.27.85", "_attr_direction_status"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],
    "sensor_door": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "contact",
                "device_class": CoverDeviceClass.DOOR,
            },
            MK_RESOURCES: {
                "status": ("3.1.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
    ],
    "sensor_water_leak": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "moisture",
                "device_class": BinarySensorDeviceClass.MOISTURE,
            },
            MK_RESOURCES: {
                "moisture": ("3.1.85", "_attr_is_on"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
    ],
    "sensor_smoke": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "smoke",
                "device_class": BinarySensorDeviceClass.SMOKE,
            },
            MK_RESOURCES: {"smoke": ("13.1.85", "_attr_is_on")},
        }},
    ],

    # ---- Locks ----
    "lock_p100": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "contact",
                "device_class": CoverDeviceClass.DOOR,
            },
            MK_RESOURCES: {"status": ("13.12.85", "_attr_native_value")},
        }},
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "contact",
                "device_class": "",
                "state_class": None,
                "unit_of_measurement": "",
            },
            MK_RESOURCES: {"status": ("13.2.85", "_attr_native_value")},
        }},
    ],
    "lock_a100pro": [
        {"sensor": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "lock_state"},
            MK_RESOURCES: {
                "lock_state": ("13.88.85", "_attr_native_value"),
                "open_door_method_id": ("13.18.85", "_attr_open_door_method"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "door",
                "device_class": CoverDeviceClass.DOOR,
            },
            MK_RESOURCES: {"door_event": ("13.17.85", "_attr_native_value")},
        }},
    ],

    # ---- Curtains ----
    "cover_curtain_battery": [
        {"cover": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "curtain"},
            MK_RESOURCES: {
                "position": ("1.1.85", "_attr_current_cover_position"),
                "curtain_status": ("14.4.85", "_attr_curtain_running_status"),
                "set_mode": ("14.8.85", "_attr_set_mode"),
            },
        }},
        SENSOR_BATTERY,
    ],
    "cover_curtain": [
        {"cover": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "curtain"},
            MK_RESOURCES: {
                "position": ("1.1.85", "_attr_current_cover_position"),
                "curtain_status": ("14.4.85", "_attr_curtain_running_status"),
                "set_mode": ("14.2.85", "_attr_set_mode"),
            },
        }},
    ],

    # ---- Cube ----
    "cube": [
        {"sensor": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "action"},
            MK_RESOURCES: {
                "cube_status": ("13.1.85", "_attr_native_value"),
                "rotate_degree": ("0.3.85", "_attr_rotate_degree"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],

    # ---- Brightness-only lights (no color temp) ----
    "light_brightness_only": [
        {"light": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "light",
                "color_mode": ColorMode.BRIGHTNESS,
                "supported_color_mode": [ColorMode.BRIGHTNESS],
            },
            MK_RESOURCES: {
                "toggle": ("4.1.85", "_attr_is_on"),
                "brightness": ("14.1.85", "_attr_brightness"),
            },
        }},
    ],

    # ---- Vibration sensors ----
    "sensor_vibration": [
        {"sensor": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "action"},
            MK_RESOURCES: {
                "vibration": ("13.1.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
                "voltage": ("8.0.2008", "_attr_voltage"),
            },
        }},
    ],
    "sensor_vibration_t1": [
        {"sensor": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "action"},
            MK_RESOURCES: {
                "knock": ("13.3.85", "_attr_native_value"),
                "move": ("13.7.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],

    # ---- Gas sensor ----
    "sensor_gas": [
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "gas_density",
                "state_class": "measurement",
            },
            MK_RESOURCES: {
                "gas_density": ("0.5.85", "_attr_native_value"),
                "zigbee_lqi": ("8.0.2007", "_attr_zigbee_lqi"),
            },
        }},
    ],

    # ---- Illuminance sensor with battery ----
    "sensor_illuminance_battery": [
        SENSOR_ILLUMINANCE,
        SENSOR_BATTERY,
    ],

    # ---- Presence sensors (FP1E/FP2/FP300) ----
    "sensor_presence_fp2": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "exist",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "exist": ("3.51.85", "_attr_native_value"),
            },
        }},
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "illuminance",
                "device_class": SensorDeviceClass.ILLUMINANCE,
                "state_class": "measurement",
                "unit_of_measurement": LIGHT_LUX,
            },
            MK_RESOURCES: {"illumination": ("0.4.85", "_attr_native_value")},
        }},
    ],
    "sensor_presence_fp300": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "exist",
                "device_class": BinarySensorDeviceClass.MOTION,
            },
            MK_RESOURCES: {
                "exist": ("3.51.85", "_attr_native_value"),
            },
        }},
        SENSOR_TEMPERATURE,
        SENSOR_HUMIDITY,
        SENSOR_ILLUMINANCE,
    ],

    # ---- Door locks ----
    "lock_generic": [
        {"binary_sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "door",
                "device_class": CoverDeviceClass.DOOR,
            },
            MK_RESOURCES: {
                "door_event": ("13.17.85", "_attr_native_value"),
            },
        }},
    ],

    # ---- Climate ----
    "climate_thermostat": [
        {"climate": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "thermostat",
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
            },
            MK_RESOURCES: {
                "on_off_status": ("3.1.85", "_attr_on_off_status"),
                "set_mode": ("14.2.85", "_attr_set_mode"),
            },
        }},
    ],
    "climate_thermostat_temp": [
        {"climate": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "thermostat",
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
            },
            MK_RESOURCES: {
                "on_off_status": ("3.1.85", "_attr_on_off_status"),
                "set_mode": ("14.2.85", "_attr_set_mode"),
                "temperature_value": ("0.1.85", "_attr_current_temperature"),
            },
        }},
    ],
    "climate_radiator": [
        {"climate": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "thermostat",
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
            },
            MK_RESOURCES: {
                "on_off_status": ("4.21.85", "_attr_on_off_status"),
                "set_temperature": ("1.8.85", "_attr_target_temperature"),
                "temperature_value": ("0.1.85", "_attr_current_temperature"),
            },
        }},
        SENSOR_BATTERY,
    ],
    "climate_ac_old": [
        {"climate": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "climate",
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
            },
            MK_RESOURCES: {
                "ac_zip_status": ("14.10.85", "_attr_ac_zip_status"),
                "on_off_status": ("3.1.85", "_attr_on_off_status"),
                "temperature_value": ("0.1.85", "_attr_current_temperature"),
            },
        }},
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "power",
                "device_class": SensorDeviceClass.POWER,
                "state_class": "measurement",
                "unit_of_measurement": UnitOfPower.WATT,
            },
            MK_RESOURCES: {"ac_load_power": ("0.11.85", "_attr_native_value")},
        }},
        SENSOR_ENERGY,
    ],
    "climate_p3": [
        {"climate": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "climate",
                "unit_of_measurement": UnitOfTemperature.CELSIUS,
            },
            MK_RESOURCES: {
                "ac_zip_status": ("14.32.85", "_attr_ac_zip_status"),
                "send_ac_cmd": ("8.0.2116", "_attr_send_ac_cmd"),
                "on_off_status": ("3.1.85", "_attr_on_off_status"),
                "temperature_value": ("0.1.85", "_attr_current_temperature"),
            },
        }},
        SENSOR_HUMIDITY,
        {"sensor": {
            MK_INIT_PARAMS: {
                MK_HASS_NAME: "power",
                "device_class": SensorDeviceClass.POWER,
                "state_class": "measurement",
                "unit_of_measurement": UnitOfPower.WATT,
            },
            MK_RESOURCES: {"ac_load_power": ("0.11.85", "_attr_native_value")},
        }},
        SENSOR_ENERGY,
        {"switch": {
            MK_INIT_PARAMS: {MK_HASS_NAME: "relay"},
            MK_RESOURCES: {"toggle": ("4.1.85", "_attr_is_on")},
        }},
    ],
}

# ======================== Model registry ========================
# Format: model: (manufacturer, name, hw_version, template_name[, overrides])

MODEL_REGISTRY = {
    # ---- Gateways (M1S with light) ----
    "lumi.gateway.aeu01":   ("Aqara", "Gateway M1S", "ZHWG15LM", "gateway_m1s"),
    "lumi.gateway.acn01":   ("Aqara", "Gateway M1S", "ZHWG15LM", "gateway_m1s"),
    "lumi.gateway.acn004":  ("Aqara", "Gateway M1S 22", "ZHWG15LM", "gateway_m1s"),
    "lumi.gateway.agl002":  ("Aqara", "Gateway M1S Gen2", "ZHWG15LM", "gateway_m1s"),
    "lumi.gateway.aqhm02":  ("Aqara", "Gateway", "ZHWG15LM", "gateway_m1s"),
    "lumi.gateway.aqhm01":  ("Aqara", "Gateway", "ZHWG15LM", "gateway_m1s"),
    # ---- Gateways (no params) ----
    "lumi.gateway.sacn01":  ("Aqara", "Smart Hub H1", "QBCZWG11LM", "gateway_no_params"),
    "lumi.gateway.aqcn02":  ("Aqara", "Hub E1", "ZHWG16LM", "gateway_no_params"),
    "lumi.gateway.iragl01": ("Aqara", "GateWay M2", "", "gateway_no_params"),
    "lumi.gateway.iragl5":  ("Aqara", "GateWay M2", "", "gateway_no_params"),
    "lumi.gateway.iragl7":  ("Aqara", "GateWay M2", "", "gateway_no_params"),
    "lumi.gateway.iragl8":  ("Aqara", "GateWay M2 22", "", "gateway_no_params"),
    "lumi.gateway.aq1":     ("Aqara", "GateWay M2", "", "gateway_no_params"),

    # ---- Wall switches: single key, neutral wire (with power) ----
    "lumi.ctrl_ln1.v1":     ("Aqara", "Wall Switch (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.acn029":   ("Aqara", "Wall Switch H1M (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.acn004":   ("Aqara", "Wall Switch X1 (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.n1acn1":   ("Aqara", "Wall Switch H1 (Single Rocker)", "QBKG27LM", "switch_1_neutral"),
    "lumi.switch.b1nacn01": ("Aqara", "Wall Switch T1 (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.b1nacn02": ("Aqara", "Wall Switch D1 (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.b1nc01":   ("Aqara", "Wall Switch E1 (Single Rocker)", "", "switch_1_neutral"),
    # ---- Wall switches: single key, no neutral wire ----
    "lumi.ctrl_neutral1.v1": ("Aqara", "Wall Switch (Single Rocker)", "QBKG04LM", "switch_1_no_neutral"),
    "lumi.switch.acn001":   ("Aqara", "Wall Switch X1 (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.switch.l1acn1":   ("Aqara", "Wall Switch H1 (Single Rocker)", "QBKG27LM", "switch_1_no_neutral"),
    "lumi.switch.b1lacn01": ("Aqara", "Wall Switch T1 (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.switch.b1lacn02": ("Aqara", "Wall Switch D1 (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.switch.b1lc04":   ("Aqara", "Wall Switch E1 (Single Rocker)", "", "switch_1_no_neutral"),

    # ---- Wall switches: double key, neutral wire ----
    "lumi.ctrl_ln2.v1":     ("Aqara", "Wall Switch (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn030":   ("Aqara", "Wall Switch H1M (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn005":   ("Aqara", "Wall Switch X1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.n2acn1":   ("Aqara", "Wall Switch H1 (Double Rocker)", "QBKG27LM", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.b2nacn01": ("Aqara", "Wall Switch T1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.b2nacn02": ("Aqara", "Wall Switch D1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.b2nc01":   ("Aqara", "Wall Switch E1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    # ---- Wall switches: double key, no neutral wire ----
    "lumi.ctrl_neutral2.v1": ("Aqara", "Wall Switch (Double Rocker)", "QBKG04LM", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.acn002":   ("Aqara", "Wall Switch X1 (Double Rocker)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.l2acn1":   ("Aqara", "Wall Switch H1 (Double Rocker)", "QBKG28LM", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.b2lacn01": ("Aqara", "Wall Switch T1 (Double Rocker)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.b2lacn02": ("Aqara", "Wall Switch D1 (Double Rocker)", "QBKG21LM", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.b2lc04":   ("Aqara", "Wall Switch E1 (Double Rocker)", "QBKG21LM", "switch_multi_no_neutral", {"ch_count": 2}),

    # ---- Wall switches: triple key, neutral wire ----
    "lumi.switch.acn031":   ("Aqara", "Wall Switch H1M (Three Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.acn006":   ("Aqara", "Wall Switch X1 (Three Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.n3acn1":   ("Aqara", "Wall Switch H1 (Three Rocker)", "QBKG27LM", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.b3n01":    ("Aqara", "Wall Switch T1 (Three Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.n4acn4":   ("Aqara", "screen panel S1 (Three Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    # ---- Wall switches: triple key, no neutral wire ----
    "lumi.switch.acn003":   ("Aqara", "Wall Switch X1 (Three Rocker)", "", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.l3acn1":   ("Aqara", "Wall Switch H1 (Three Rocker)", "QBKG29LM", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.b3l01":    ("Aqara", "Wall Switch T1 (Three Rocker)", "", "switch_multi_no_neutral", {"ch_count": 3}),

    # ---- Plugs / Outlets / Control modules ----
    "lumi.switch.l0acn1":   ("Aqara", "Wall Switch (Single Rocker)", "", "plug_with_power"),
    "lumi.switch.n0acn2":   ("Aqara", "Wall Switch (Single Rocker)", "", "plug_with_power"),
    "lumi.plug.v1":         ("Xiaomi", "Plug", "ZNCZ02LM", "plug_with_power"),
    "lumi.plug.aq1":        ("Xiaomi", "Plug", "", "plug_with_power"),
    "lumi.plug.macn01":     ("Aqara", "Plug T1", "", "plug_with_power"),
    "lumi.plug.acn003":     ("Aqara", "Smart Wall Outlet X1(USB)", "", "plug_with_power"),
    "lumi.plug.sacn03":     ("Aqara", "Smart Wall Outlet H1(USB)", "QBCZWG11LM", "plug_with_power"),
    "lumi.plug.sacn02":     ("Aqara", "Smart Wall Outlet H1", "QBCZWG11LM", "plug_with_power"),

    # ---- Lights ----
    "lumi.light.aqcn02":    ("Aqara", "Bulb", "ZNLDP12LM", "light_cct_14x"),
    "lumi.light.cwopcn02":  ("Aqara", "Opple MX650", "XDD12LM", "light_cct_14x"),
    "lumi.light.cwopcn03":  ("Aqara", "Opple MX480", "XDD13LM", "light_cct_14x"),
    "lumi.light.cwacn1":    ("Aqara", "0-10V Dimmer", "ZNTGMK12LM", "light_cct_14x"),
    "lumi.light.cwjwcn01":  ("Aqara", "Jiawen 0-12V Dimmer", "Z204", "light_cct_14x"),
    "lumi.light.acn008":    ("Aqara", "H1 LED Light", "", "light_cct_14x"),
    "lumi.light.cwac02":    ("Aqara", "Bulb T1", "ZNLDP13LM", "light_cct_1x"),
    "lumi.light.rgbac1":    ("Aqara", "RGBW LED Controller T1", "ZNTGMK11LM", "light_rgb"),
    "lumi.dimmer.rcbac1":   ("Aqara", "RGBW LED Dimmer", "ZNDDMK11LM", "light_rgbw_dimmer"),

    # ---- Wireless buttons: single ----
    "lumi.remote.b186acn01": ("Aqara", "Single Wall Button", "WXKG03LM", "button_single"),
    "lumi.remote.b1acn01":  ("Aqara", "Wireless Remote Switch (Single Rocker)", "", "button_single"),
    "lumi.sensor_switch.aq3": ("Aqara", "Wireless Remote Switch Plus (Single Rocker)", "", "button_single"),
    "lumi.remote.b18ac1":   ("Aqara", "Wireless Remote Switch H1 (Single Rocker)", "WXKG14LM", "button_single"),
    "lumi.remote.b1acn02":  ("Aqara", "Wireless Remote Switch E1 (Single Rocker)", "WXKG12LM", "button_single"),
    "lumi.remote.acn003":   ("Aqara", "Wireless Remote Switch E1 (Single Rocker)", "WXKG16LM", "button_single"),
    "lumi.remote.b186acn02": ("Aqara", "Wireless Remote Switch D1 (Single Rocker)", "WXKG06LM", "button_single"),
    "lumi.remote.b186acn03": ("Aqara", "Wireless Remote Switch T1 (Single Rocker)", "", "button_single"),
    "lumi.remote.acn007":   ("Aqara", "Single Wall Button E1", "WXKG20LM", "button_single"),
    # ---- Wireless buttons: double ----
    "lumi.remote.b286acn01": ("Aqara", "Double Wall Button", "WXKG02LM", "button_multi", {"ch_count": 2}),
    "lumi.remote.b28ac1":   ("Aqara", "Wireless Remote Switch H1 (Double Rocker)", "WXKG15LM", "button_multi", {"ch_count": 2}),
    "lumi.remote.acn004":   ("Aqara", "Wireless Remote Switch E1 (Double Rocker)", "WXKG17LM", "button_multi", {"ch_count": 2}),
    "lumi.remote.b286acn02": ("Aqara", "Wireless Remote Switch D1 (Double Rocker)", "WXKG07LM", "button_multi", {"ch_count": 2}),
    "lumi.remote.b286acn03": ("Aqara", "Wireless Remote Switch T1 (Double Rocker)", "", "button_multi", {"ch_count": 2}),
    # ---- Wireless buttons: four ----
    "lumi.remote.b486opcn01": ("Aqara", "Wireless Remote Switch (Four Rocker)", "", "button_multi", {"ch_count": 4}),
    # ---- Wireless buttons: rotary ----
    "lumi.remote.rkba01":   ("Aqara", "Wireless rotary switch H1", "", "button_rotary"),

    # ---- Temperature & Humidity sensors ----
    "lumi.sensor_ht.v1":    ("Xiaomi", "TH Sensor", "WSDCGQ01LM", "sensor_th"),
    "lumi.sensor_ht.agl02": ("Aqara", "T1 TH Sensor", "", "sensor_th_pressure"),
    "lumi.weather.v1":      ("Aqara", "TH Sensor", "WSDCGQ11LM", "sensor_th_pressure"),

    # ---- Motion sensors ----
    "lumi.sensor_motion.v1": ("Xiaomi", "Motion Sensor", "RTCGQ01LM", "sensor_motion"),
    "lumi.sensor_motion.v2": ("Xiaomi", "Motion Sensor", "RTCGQ01LM", "sensor_motion"),
    "lumi.sensor_motion.aq2": ("Aqara", "Motion Sensor", "RTCGQ11LM", "sensor_motion_lux"),
    "lumi.motion.agl04":    ("Aqara", "Precision Motion Sensor", "RTCGQ13LM", "sensor_motion_precision"),
    "lumi.motion.ac01":     ("Aqara", "Presence Sensor FP1", "RTCZCGQ11LM", "sensor_presence_fp1"),

    # ---- Door / Window sensors ----
    "lumi.sensor_magnet.v1": ("Xiaomi", "Door Sensor", "MCCGQ01LM", "sensor_door"),
    "lumi.sensor_magnet.v2": ("Xiaomi", "Door Sensor", "MCCGQ01LM", "sensor_door"),
    "lumi.sensor_magnet.aq2": ("Aqara", "Door Sensor", "MCCGQ11LM", "sensor_door"),
    "lumi.magnet.agl02":    ("Aqara", "Door Sensor T1", "MCCGQ12LM", "sensor_door"),
    "lumi.magnet.acn001":   ("Aqara", "Door Sensor E1", "MCCGQ14LM", "sensor_door"),
    "lumi.magnet.ac01":     ("Aqara", "Door Sensor P1", "MCCGQ13LM", "sensor_door"),

    # ---- Water leak sensors ----
    "lumi.sensor_wleak.aq1": ("Aqara", "Water Leak Sensor", "SJCGQ11LM", "sensor_water_leak"),
    "lumi.sensor_wleak.v1": ("Aqara", "Water Leak Sensor", "", "sensor_water_leak"),
    "lumi.flood.agl02":     ("Aqara", "Water Leak Sensor T1", "SJCGQ12LM", "sensor_water_leak"),
    "lumi.flood.acn001":    ("Aqara", "Water Leak Sensor E1", "SJCGQ13LM", "sensor_water_leak"),

    # ---- Smoke sensors ----
    "lumi.sensor_smoke.v1":  ("Xiaomi", "Smoke Sensor", "JTYJ-GD-01LM/BW", "sensor_smoke"),
    "lumi.sensor_smoke.acn03": ("Xiaomi", "Smoke Sensor", "", "sensor_smoke"),

    # ---- Locks ----
    "aqara.lock.wbzac1":    ("Aqara", "DoorLock P100", "", "lock_p100"),
    "aqara.lock.acn001":    ("Aqara", "Smart Door Lock A100 Pro", "", "lock_a100pro"),

    # ---- Curtains ----
    "lumi.curtain.acn003":  ("Aqara", "Curtain Motor E1", "ZNCLDJ14LM", "cover_curtain_battery"),

    # ---- Cube ----
    "lumi.sensor_cube.aqgl01": ("Aqara", "Magic Cube Controller", "MFKZQ01LM", "cube"),

    # ---- Curtains (new) ----
    "lumi.curtain.v1":      ("Aqara", "Curtain Controller", "", "cover_curtain"),
    "lumi.curtain.aq2":     ("Aqara", "Roller Shade Controller", "", "cover_curtain"),
    "lumi.curtain.acn002":  ("Aqara", "Roller Shade Driver E1", "", "cover_curtain"),
    "lumi.curtain.acn004":  ("Aqara", "Curtain Controller X1", "", "cover_curtain"),
    "lumi.curtain.acn007":  ("Aqara", "Curtain Motor T1", "", "cover_curtain"),
    "lumi.curtain.acn014":  ("Aqara", "Smart Curtain Controller E1", "", "cover_curtain"),
    "lumi.curtain.acn015":  ("Aqara", "Smart Curtain Controller T2", "", "cover_curtain"),
    "lumi.curtain.acn018":  ("Aqara", "Curtain Controller C200", "", "cover_curtain"),
    "lumi.curtain.acn04":   ("Aqara", "Smart Curtain Controller C3", "", "cover_curtain"),
    "lumi.curtain.hagl04":  ("Aqara", "Curtain Controller B1", "", "cover_curtain_battery"),
    "lumi.curtain.hagl07":  ("Aqara", "Curtain Controller C2", "", "cover_curtain"),
    "lumi.curtain.hagl08":  ("Aqara", "Curtain Controller A1", "", "cover_curtain"),
    "lumi.curtain.jcn001":  ("Aqara", "Curtain Controller L", "", "cover_curtain"),
    "lumi.curtain.vagl02":  ("Aqara", "Roller Shade Controller T1", "", "cover_curtain"),

    # ---- Cube (new) ----
    "lumi.sensor_cube.v1":  ("Xiaomi", "Cube", "", "cube"),
    "lumi.remote.cagl01":   ("Aqara", "Cube T1", "", "cube"),
    "lumi.remote.cagl02":   ("Aqara", "Cube T1 Pro", "", "cube"),
    "lumi.remote.jcn001":   ("Aqara", "Cube L", "", "cube"),

    # ---- Climate ----
    "lumi.aircondition.acn05": ("Aqara", "Air Conditioning Companion P3", "KTBL12LM", "climate_p3"),
    "lumi.acpartner.v3":    ("Aqara", "AC Controller (Advanced)", "", "climate_ac_old"),
    "lumi.acpartner.aq1":   ("Aqara", "AC Companion (B-end)", "", "climate_ac_old"),
    "lumi.acpartner.es1":   ("Aqara", "AC Companion (B-end)", "", "climate_ac_old"),
    "lumi.airrtc.tcpecn01": ("Aqara", "Thermostat", "", "climate_thermostat"),
    "lumi.airrtc.tcpecn02": ("Aqara", "Thermostat S2", "", "climate_thermostat"),
    "lumi.ctrl_hvac.aq1":   ("Aqara", "Thermostat", "", "climate_thermostat"),
    "lumi.ctrl_hvac.es1":   ("Aqara", "Thermostat", "", "climate_thermostat"),
    "lumi.airrtc.tcpco2ecn01": ("Aqara", "Thermostat (CO2)", "", "climate_thermostat_temp"),
    "lumi.airrtc.agl001":   ("Aqara", "Smart Radiator Thermostat E1", "", "climate_radiator"),
    "lumi.airrtc.pcacn2":   ("Aqara", "Thermostat S3", "", "climate_thermostat_temp"),
    "lumi.airrtc.pcacn2_thermostat": ("Aqara", "Thermostat S3", "", "climate_thermostat_temp"),
    "aqara.airrtc.ecn001":  ("Aqara", "VRF Controller T1/Lite", "", "climate_thermostat"),
    "lumi.airrtc.vrfegl01": ("Aqara", "VRF Air Conditioning Controller", "", "climate_thermostat"),
    "lumi.airrtc.acn002":   ("Aqara", "Thermostat W400 (VRF)", "", "climate_thermostat_temp"),
    "lumi.airrtc.acn003":   ("Aqara", "Thermostat W400 (FCU)", "", "climate_thermostat_temp"),

    # ---- Door locks (new) ----
    "aqara.lock.eicn01":    ("Aqara", "Smart Door Lock A100", "", "lock_generic"),
    "aqara.lock.acn002":    ("Aqara", "Smart Door Lock Star", "", "lock_a100pro"),
    "lumi.lock.acn02":      ("Aqara", "Smart Door Lock S2", "", "lock_generic"),
    "lumi.lock.acn03":      ("Aqara", "Smart Door Lock S2 Pro", "", "lock_generic"),
    "lumi.lock.acn04":      ("Aqara", "Smart Door Lock HL", "", "lock_generic"),
    "lumi.lock.aq1":        ("Aqara", "Smart Door Lock", "", "lock_generic"),

    # ---- Gateways (new) ----
    "lumi.gateway.acn008":  ("Aqara", "Hub M1S series 2", "", "gateway_m1s"),
    "lumi.gateway.acn011":  ("Aqara", "Smart Wall Hub V1", "", "gateway_no_params"),
    "lumi.gateway.acn012":  ("Aqara", "Hub M3", "", "gateway_no_params"),
    "lumi.gateway.agl004":  ("Aqara", "Hub M3 (International)", "", "gateway_no_params"),
    "lumi.gateway.agl010":  ("Aqara", "Hub M100", "", "gateway_no_params"),
    "lumi.gateway.agl011":  ("Aqara", "Hub M200", "", "gateway_no_params"),
    "lumi.gateway.agl015":  ("Aqara", "Panel Hub AX100S", "", "gateway_no_params"),
    "lumi.gateway.jcn001":  ("Aqara", "Hub L", "", "gateway_no_params"),
    "lumi.gateway.jcn002":  ("Aqara", "Hub L-02", "", "gateway_no_params"),
    "lumi.gateway.rj45ecn01": ("Aqara", "Hub", "", "gateway_no_params"),

    # ---- Wall switches (new) ----
    "lumi.ctrl_ln1.es1":    ("Aqara", "Wall Switch (Single Rocker)", "", "switch_1_neutral"),
    "lumi.ctrl_ln1.aq1":    ("Aqara", "Wall Switch (Single Rocker)", "", "switch_1_neutral"),
    "lumi.ctrl_neutral1.aq1": ("Aqara", "Wall Switch (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.ctrl_neutral1.es1": ("Aqara", "Wall Switch (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.ctrl_ln2.es1":    ("Aqara", "Wall Switch (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.ctrl_ln2.aq1":    ("Aqara", "Wall Switch (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.ctrl_neutral2.aq1": ("Aqara", "Wall Switch (Double Rocker)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.ctrl_neutral2.es1": ("Aqara", "Wall Switch (Double Rocker)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.acn040":   ("Aqara", "Wall Switch E1 (Triple Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.acn041":   ("Aqara", "Wall Switch J1 (Single Rocker)", "", "switch_1_no_neutral"),
    "lumi.switch.acn042":   ("Aqara", "Wall Switch J1 (Double Rocker)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.acn043":   ("Aqara", "Wall Switch J1 (Triple Rocker)", "", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.acn044":   ("Aqara", "Wall Switch J1 (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.acn045":   ("Aqara", "Wall Switch J1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn046":   ("Aqara", "Wall Switch J1 (Triple Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.acn047":   ("Aqara", "Dual Relay Module T2", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn048":   ("Aqara", "Wall Switch Z1 (Single Rocker)", "", "plug_with_power"),
    "lumi.switch.acn049":   ("Aqara", "Wall Switch Z1 (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn051":   ("Aqara", "Magic Switch V1 (Quad Rocker)", "", "switch_multi_neutral", {"ch_count": 4}),
    "lumi.switch.acn054":   ("Aqara", "Wall Switch Z1 (Triple Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.acn055":   ("Aqara", "Wall Switch Z1 (Quad Rocker)", "", "switch_multi_neutral", {"ch_count": 4}),
    "lumi.switch.acn056":   ("Aqara", "Wall Switch Z1 Pro (Single)", "", "switch_1_no_neutral"),
    "lumi.switch.acn057":   ("Aqara", "Wall Switch Z1 Pro (Double)", "", "switch_multi_no_neutral", {"ch_count": 2}),
    "lumi.switch.acn058":   ("Aqara", "Wall Switch Z1 Pro (Triple)", "", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.acn059":   ("Aqara", "Wall Switch Z1 Pro (Quad)", "", "switch_multi_no_neutral", {"ch_count": 4}),
    "lumi.switch.acn062":   ("Aqara", "Wall Switch Q1 (Single)", "", "plug_with_power"),
    "lumi.switch.acn063":   ("Aqara", "Wall Switch Q1 (Double)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.acn065":   ("Aqara", "Wall Switch Q1 (Quad)", "", "switch_multi_neutral", {"ch_count": 4}),
    "lumi.switch.jcn001":   ("Aqara", "Wall Switch L (Single Rocker)", "", "switch_1_neutral"),
    "lumi.switch.jcn002":   ("Aqara", "Wall Switch L (Double Rocker)", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.switch.jcn004":   ("Aqara", "Wall Switch L (Triple Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.l3acn3":   ("Aqara", "Wall Switch D1 (Triple Rocker)", "", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.n3acn3":   ("Aqara", "Wall Switch D1 (Triple Rocker)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.n0agl1":   ("Aqara", "Switch Module T1 (International)", "", "plug_with_power"),
    "lumi.switch.rkna01":   ("Aqara", "Smart Knob H1 (With Neutral)", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.switch.acn032":   ("Aqara", "Magic Switch S1E", "", "switch_multi_no_neutral", {"ch_count": 3}),
    "lumi.switch.acn034":   ("Aqara", "MagicPad S1 Plus", "", "switch_multi_neutral", {"ch_count": 3}),
    "lumi.ctrl_dualchn.es1": ("Aqara", "Dual Control Module", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.relay.c2acn01":   ("Aqara", "Dual Control Module", "", "switch_multi_neutral", {"ch_count": 2}),
    "lumi.relay.c4acn01":   ("Aqara", "Relay Controller (4ch)", "", "switch_multi_neutral", {"ch_count": 4}),
    "virtual.controller.a4acn4": ("Aqara", "Virtual Child Device-Switch", "", "switch_1_no_neutral"),
    "aqara.gateway.mdcn01": ("Aqara", "Manton Micro-Breaker S3", "", "switch_1_no_neutral"),
    "aqara.pr_tran.eicn01": ("Aqara", "Manton Breaker 485", "", "plug_with_power"),

    # ---- Plugs / Outlets (new) ----
    "lumi.ctrl_86plug.aq1": ("Aqara", "Wall Outlet", "", "plug_with_power"),
    "lumi.ctrl_86plug.es1": ("Aqara", "Wall Outlet", "", "plug_with_power"),
    "lumi.ctrl_86plug.v1":  ("Aqara", "Wall Outlet", "", "plug_with_power"),
    "lumi.plug.es1":        ("Aqara", "Smart Plug (China)", "", "plug_with_power"),
    "lumi.plug.maeu01":     ("Aqara", "Smart Plug EU", "", "plug_with_power"),
    "lumi.plug.maus01":     ("Aqara", "Smart Plug (USA)", "", "plug_with_power"),
    "lumi.plug.sgwacn01":   ("Aqara", "Wall Outlet Hub", "", "plug_with_power"),
    "lumi.plug.acn005":     ("Aqara", "Smart Wall Socket H2", "", "plug_with_power"),

    # ---- Lights (new) ----
    "lumi.light.acn003":    ("Aqara", "Ceiling Light L1-350", "", "light_cct_1x"),
    "lumi.light.acn004":    ("Aqara", "Dimmer Controller T1 Pro", "", "light_cct_14x"),
    "lumi.light.acn006":    ("Aqara", "Track Light H1 Pro", "", "light_cct_14x"),
    "lumi.light.acn007":    ("Aqara", "Grille Light (6-Lamp)", "", "light_brightness_only"),
    "lumi.light.acn009":    ("Aqara", "Flood Light (30cm)", "", "light_brightness_only"),
    "lumi.light.acn010":    ("Aqara", "Flood Light (60cm)", "", "light_brightness_only"),
    "lumi.light.acn011":    ("Aqara", "Pendant Light", "", "light_brightness_only"),
    "lumi.light.acn012":    ("Aqara", "Foldable Grille Light (6-Lamp)", "", "light_brightness_only"),
    "lumi.light.acn013":    ("Aqara", "Wall Washer Light (22cm)", "", "light_brightness_only"),
    "lumi.light.acn014":    ("Aqara", "LED Bulb T1 (Tunable White)", "", "light_cct_1x"),
    "lumi.light.acn015":    ("Aqara", "Light Art Skylight H1", "", "light_cct_1x"),
    "lumi.light.acn023":    ("Aqara", "Spotlight T2 (15)", "", "light_cct_14x"),
    "lumi.light.acn024":    ("Aqara", "Spotlight T2 (24)", "", "light_cct_14x"),
    "lumi.light.acn025":    ("Aqara", "Spotlight T2 (36)", "", "light_cct_14x"),
    "lumi.light.acn026":    ("Aqara", "Downlight T2 (60)", "", "light_cct_14x"),
    "lumi.light.acn032":    ("Aqara", "Ceiling Light T1M", "", "light_cct_1x"),
    "lumi.light.acn036":    ("Aqara", "Spotlight V1", "", "light_brightness_only"),
    "lumi.light.acn037":    ("Aqara", "Track Light V1", "", "light_cct_1x"),
    "lumi.light.acn128":    ("Aqara", "Down/Spot Light T3", "", "light_cct_14x"),
    "lumi.light.acn132":    ("Aqara", "LED Strip T1", "", "light_cct_1x"),
    "lumi.light.agl001":    ("Aqara", "LED Bulb T2 (E26, RGB CCT)", "", "light_cct_1x"),
    "lumi.light.agl002":    ("Aqara", "LED Bulb T2 (E26, CCT)", "", "light_cct_1x"),
    "lumi.light.agl003":    ("Aqara", "LED Bulb T2 (E27, RGB CCT)", "", "light_cct_1x"),
    "lumi.light.agl004":    ("Aqara", "LED Bulb T2 (E27, CCT)", "", "light_cct_1x"),
    "lumi.light.cbacn1":    ("Aqara", "Constant Current Driver T1-1", "", "light_brightness_only"),
    "lumi.light.cwopcn01":  ("Aqara", "Ceiling Light MX960", "", "light_cct_14x"),
    "lumi.light.cwjwcn02":  ("Aqara", "Down Light (CCT)", "", "light_cct_14x"),
    "lumi.light.wjwcn01":   ("Aqara", "Spot Light (Brightness)", "", "light_brightness_only"),
    "lumi.ctrl_rgb.aq1":    ("Aqara", "Dimmer (Multicolor)", "", "light_rgb"),
    "lumi.ctrl_rgb.es1":    ("Aqara", "Dimmer (Multicolor)", "", "light_rgb"),
    "lumi.dimmer.rgbegl01": ("Aqara", "Dimmer (Multicolor)", "", "light_rgb"),
    "lumi.dimmer.acn001":   ("Aqara", "Constant Current Driver T2", "", "light_cct_1x"),
    "lumi.dimmer.acn002":   ("Aqara", "Constant Current Driver T2 (24W)", "", "light_cct_1x"),
    "lumi.dimmer.acn003":   ("Aqara", "Constant Voltage Driver T1", "", "light_cct_1x"),
    "lumi.dimmer.acn004":   ("Aqara", "Constant Voltage Driver T1 (120W)", "", "light_cct_1x"),
    "lumi.dimmer.acn005":   ("Aqara", "Constant Voltage Driver T1 (240W)", "", "light_cct_1x"),
    "lumi.dimmer.c3egl01":  ("Aqara", "Dimmer (3 Channels)", "", "light_cct_14x"),

    # ---- Wireless buttons (new) ----
    "lumi.remote.acn011":   ("Aqara", "Wireless Switch J1 (Single)", "", "button_single"),
    "lumi.remote.acn012":   ("Aqara", "Wireless Switch J1 (Double)", "", "button_multi", {"ch_count": 2}),
    "lumi.remote.b286opcn01": ("Aqara", "Scene Switch (Two Button)", "", "button_multi", {"ch_count": 2}),
    "lumi.remote.b686opcn01": ("Aqara", "Scene Switch (Six Button)", "", "button_multi", {"ch_count": 6}),
    "lumi.remote.jcn002":   ("Aqara", "Wireless Switch L", "", "button_single"),
    "lumi.sensor_switch.v1": ("Xiaomi", "Wireless Switch", "", "button_single"),
    "lumi.sensor_switch.v2": ("Aqara", "Wireless Switch", "", "button_single"),
    "lumi.sensor_switch.aq2": ("Aqara", "Wireless Switch", "", "button_single"),
    "lumi.sensor_86sw1.v1": ("Xiaomi", "Remote Switch (Single)", "", "button_single"),
    "lumi.sensor_86sw2.v1": ("Xiaomi", "Remote Switch (Double)", "", "button_multi", {"ch_count": 2}),

    # ---- Sensors (new) ----
    "lumi.sensor_ht.jcn001": ("Aqara", "TH Sensor L", "", "sensor_th"),
    "lumi.sensor_ht.agl001": ("Aqara", "Climate Sensor W100", "", "sensor_th"),
    "lumi.magnet.acn002":   ("Aqara", "Door Sensor NB-IOT", "", "sensor_door"),
    "lumi.magnet.jcn002":   ("Aqara", "Door Sensor L", "", "sensor_door"),
    "lumi.flood.jcn001":    ("Aqara", "Water Leak Sensor L", "", "sensor_water_leak"),
    "lumi.sensor_smoke.jcn01": ("Aqara", "Smoke Detector L", "", "sensor_smoke"),
    "lumi.sensor_natgas.v1": ("Xiaomi", "Natural Gas Detector", "", "sensor_smoke"),
    "lumi.sensor_gas.jcn001": ("Aqara", "Natural Gas Detector L", "", "sensor_smoke"),
    "lumi.sensor_gas.acn02": ("Aqara", "Natural Gas Detector", "", "sensor_gas"),
    "lumi.vibration.aq1":   ("Aqara", "Vibration Sensor", "", "sensor_vibration"),
    "lumi.vibration.agl01": ("Aqara", "Vibration Sensor T1", "", "sensor_vibration_t1"),
    "lumi.vibration.jcn001": ("Aqara", "Vibration Sensor L", "", "sensor_vibration_t1"),
    "lumi.sen_ill.agl01":   ("Aqara", "Light Sensor T1", "", "sensor_illuminance_battery"),
    "lumi.airmonitor.acn01": ("Aqara", "TVOC Air Quality Monitor", "", "sensor_th_pressure"),
    "lumi.airm.fhac01":     ("Aqara", "Air Quality Monitor S1", "", "sensor_th"),

    # ---- Motion / Presence sensors (new) ----
    "lumi.motion.ac02":     ("Aqara", "Motion Sensor P1", "", "sensor_motion_lux"),
    "lumi.motion.acn001":   ("Aqara", "Motion Sensor E1", "", "sensor_motion"),
    "lumi.motion.agl02":    ("Aqara", "Motion Sensor T1", "", "sensor_motion_precision"),
    "lumi.motion.jcn001":   ("Aqara", "Motion Sensor L", "", "sensor_motion_precision"),
    "lumi.motion.agl001":   ("Aqara", "Presence Sensor FP2", "", "sensor_presence_fp2"),
    "lumi.sensor_occupy.agl1": ("Aqara", "Presence Sensor FP1E", "", "sensor_presence_fp1"),
    "lumi.sensor_occupy.agl8": ("Aqara", "Presence Sensor FP300", "", "sensor_presence_fp300"),

    # ---- Valve controllers (new) ----
    "aqara.valve.acn001":   ("Aqara", "Valve Controller T1", "", "plug_with_power"),
    "lumi.valve.agl001":    ("Aqara", "Valve Controller T1", "", "switch_1_no_neutral"),
}

# ======================== Build function ========================


def build_device_mapping():
    """Build AIOT_DEVICE_MAPPING from templates and registry.

    Groups models by (template_name, overrides) and generates the same
    list-of-dicts format consumed by aiot_manager.py.
    """
    groups = {}
    for model, info in MODEL_REGISTRY.items():
        if len(info) == 5:
            mfg, name, hw, tmpl, overrides = info
        else:
            mfg, name, hw, tmpl = info
            overrides = {}
        key = (tmpl, tuple(sorted(overrides.items())))
        groups.setdefault(key, {})[model] = [mfg, name, hw]

    result = []
    for (tmpl_name, overrides_tuple), models in groups.items():
        overrides = dict(overrides_tuple)
        params = copy.deepcopy(PARAMS_TEMPLATES[tmpl_name])

        ch_count = overrides.get("ch_count")
        if ch_count:
            for p in params:
                for platform_config in p.values():
                    if not isinstance(platform_config, dict):
                        continue
                    resources = platform_config.get(MK_RESOURCES, {})
                    if any("{}" in v[0] for v in resources.values()):
                        platform_config[MK_MAPPING_PARAMS] = {
                            "ch_count": ch_count
                        }
                        break

        entry = dict(models)
        entry["params"] = params
        result.append(entry)

    return result


AIOT_DEVICE_MAPPING = build_device_mapping()

# ======================== Special devices ========================

SPECIAL_DEVICES_INFO = {
    "lumi.airrtc.vrfegl01": {
        "toggle": {0: "on", 1: "off"},
        "hvac_mode": {
            0: "heat",
            1: "cool",
            2: "auto",
            3: "dry",
            4: "fan_only",
        },
        "fan_mode": {0: "low", 1: "middle", 2: "high", 3: "auto"},
        "swing_mode": {0: "horizontal", 1: "vertical", 2: "both"},
        "swing_toggle": {1: "off"},
    }
}
