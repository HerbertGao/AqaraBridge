import time
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from .core.utils import local_zone

from .core.aiot_manager import (
    AiotManager,
    AiotEntityBase,
)
from .core.const import (
    CUBE,
    DOMAIN,
    HASS_DATA_AIOT_MANAGER,
)

TYPE = "sensor"

DATA_KEY = f"{TYPE}.{DOMAIN}"


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
    cls_entities = {
        "pm25": AiotAirQualitySensor,
        "co2e": AiotCO2eSensor,
        "tvoc_level": AiotTvocSensor,
        "air_temperature": AiotAirTempSensor,
        "air_humidity": AiotAirHumiSensor,
        "cube_status": AiotCubeSensor,
        "lock_state": AiotLockSensor,
        "default": AiotSensorEntity
    }
    await manager.async_add_entities(
        config_entry, TYPE, cls_entities, async_add_entities
    )


class AiotSensorEntity(AiotEntityBase, SensorEntity):
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_state_class = kwargs.get("state_class") or None
        self._attr_native_unit_of_measurement = kwargs.get("unit_of_measurement")
        self._extra_state_attributes.extend(["last_update_time", "last_update_at"])

    @property
    def last_update_time(self):
        return self.trigger_time

    @property
    def last_update_at(self):
        return self.trigger_dt

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "battry":
            return int(res_value)
        if res_name == "rotation_angle":
            return int(res_value)
        if res_name == "press_rotation_angle":
            return int(res_value)
        if res_name == "energy":
            return round(float(res_value) / 1000.0, 3)
        if res_name == "temperature":
            return round(int(res_value) / 100.0, 1)
        if res_name == "humidity":
            return round(int(res_value) / 100.0,1)
        return super().convert_res_to_attr(res_name, res_value)


class AiotAirSensorBase(AiotEntityBase, SensorEntity):
    """Base class for air quality sensor entities with shared resource handling."""
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_state_class = "measurement"

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "firmware_version":
            return res_value
        if res_name == "zigbee_lqi":
            return int(res_value)
        if res_name == "voltage":
            return format(float(res_value) / 1000, '.3f')
        return super().convert_res_to_attr(res_name, res_value)


class AiotAirQualitySensor(AiotAirSensorBase):
    """Air quality PM2.5 sensor."""
    pass


class AiotCO2eSensor(AiotAirSensorBase):
    """Air quality CO2e sensor."""
    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "co2e":
            return round(float(res_value), 1)
        return super().convert_res_to_attr(res_name, res_value)


class AiotTvocSensor(AiotAirSensorBase):
    """Air quality TVOC sensor."""
    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "tvoc_level":
            return int(res_value)
        return super().convert_res_to_attr(res_name, res_value)


class AiotAirTempSensor(AiotAirSensorBase):
    """Air quality temperature sensor."""
    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "temperature":
            return round(float(res_value), 1)
        return super().convert_res_to_attr(res_name, res_value)


class AiotAirHumiSensor(AiotAirSensorBase):
    """Air quality humidity sensor."""
    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "humidity":
            return round(float(res_value), 1)
        return super().convert_res_to_attr(res_name, res_value)


LOCK_STATE = {
    '1': 'unable_to_lock',
    '2': 'door_not_closed',
    '3': 'unlocked',
    '4': 'locked',
    '5': 'deadbolted',
    '6': 'just_unlocked',
    '7': 'locked_and_deadbolted',
    '8': 'door_ajar',
}

OPEN_DOOR_METHOD = {
    '0': 'fingerprint',
    '1': 'password',
    '2': 'nfc',
    '3': 'bluetooth',
    '4': 'temporary_password',
    '5': 'key',
    '6': 'dual_verification',
    '7': 'duress_fingerprint',
    '8': 'homekit',
    '9': 'face',
    '10': 'remote',
    '15': 'any',
}


class AiotLockSensor(AiotEntityBase, SensorEntity):
    """Smart lock state sensor."""
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_state_class = None
        self._attr_open_door_method = None
        self._extra_state_attributes.extend(["open_door_method", "trigger_time", "trigger_dt"])

    @property
    def open_door_method(self):
        return self._attr_open_door_method

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "lock_state":
            return LOCK_STATE.get(str(res_value), f"unknown_{res_value}")
        if res_name == "open_door_method_id":
            return OPEN_DOOR_METHOD.get(str(res_value), f"unknown_{res_value}")
        if res_name == "zigbee_lqi":
            return int(res_value)
        return super().convert_res_to_attr(res_name, res_value)


class AiotCubeSensor(AiotEntityBase, SensorEntity):
    """Magic Cube action sensor."""
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_state_class = None
        self._attr_rotate_degree = None
        self._extra_state_attributes.extend(["rotate_degree", "trigger_time", "trigger_dt"])

    @property
    def rotate_degree(self):
        return self._attr_rotate_degree

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "cube_status":
            return CUBE.get(str(res_value), str(res_value))
        if res_name == "rotate_degree":
            return round(float(res_value) * 360, 1)
        if res_name == "zigbee_lqi":
            return int(res_value)
        return super().convert_res_to_attr(res_name, res_value)