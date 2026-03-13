import time
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from .core.utils import local_zone

from .core.aiot_manager import (
    AiotManager,
    AiotEntityBase,
)
from .core.const import (
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
        "default": AiotSensorEntity
    }
    await manager.async_add_entities(
        config_entry, TYPE, cls_entities, async_add_entities
    )


class AiotSensorEntity(AiotEntityBase, SensorEntity):
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_state_class = kwargs.get("state_class")
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