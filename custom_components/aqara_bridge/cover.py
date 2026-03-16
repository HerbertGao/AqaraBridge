import logging
from homeassistant.components.cover import CoverEntity, CoverEntityFeature

from .core.aiot_manager import (
    AiotManager,
    AiotEntityBase,
)
from .core.const import DOMAIN, HASS_DATA_AIOT_MANAGER

TYPE = "cover"

_LOGGER = logging.getLogger(__name__)

DATA_KEY = f"{TYPE}.{DOMAIN}"


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
    cls_entities = {
        "default": AiotCoverEntity
    }
    await manager.async_add_entities(
        config_entry, TYPE, cls_entities, async_add_entities
    )


class AiotCoverEntity(AiotEntityBase, CoverEntity):
    # set_mode values: 0=open, 1=close, 2=stop
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_is_closed = None
        self._attr_curtain_running_status = None
        self._attr_set_mode = None

    @property
    def is_opening(self):
        return self._attr_curtain_running_status == 1

    @property
    def is_closing(self):
        return self._attr_curtain_running_status == 0

    async def async_open_cover(self, **kwargs):
        await self.async_set_resource("set_mode", 0)

    async def async_close_cover(self, **kwargs):
        await self.async_set_resource("set_mode", 1)

    async def async_stop_cover(self, **kwargs):
        await self.async_set_resource("set_mode", 2)

    async def async_set_cover_position(self, **kwargs):
        position = kwargs.get("position")
        if position is not None:
            await self.async_set_resource("position", position)

    def convert_attr_to_res(self, res_name, attr_value):
        if res_name == "position":
            return str(attr_value)
        elif res_name == "set_mode":
            return str(attr_value)
        return super().convert_attr_to_res(res_name, attr_value)

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "position":
            pos = int(float(res_value))
            self._attr_is_closed = pos == 0
            return pos
        elif res_name == "curtain_status":
            # 0=closing, 1=opening, 2=stopped, 3=hinder_stop
            return int(res_value)
        elif res_name == "set_mode":
            return int(res_value)
        return super().convert_res_to_attr(res_name, res_value)
