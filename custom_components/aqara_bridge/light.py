import logging
import homeassistant.util.color as color_util
from homeassistant.components.light import LightEntity

try:
    from homeassistant.components.light import ATTR_COLOR_TEMP_KELVIN
    USE_KELVIN = True
except ImportError:
    USE_KELVIN = False

from .core.aiot_manager import (
    AiotManager,
    AiotToggleableEntityBase,
)
from .core.const import DOMAIN, HASS_DATA_AIOT_MANAGER

TYPE = "light"
MIREDS_KELVIN_FACTOR = 1_000_000


def _kelvin_to_mireds(kelvin):
    return int(MIREDS_KELVIN_FACTOR / kelvin)


def _mireds_to_kelvin(mireds):
    return int(MIREDS_KELVIN_FACTOR / mireds)

_LOGGER = logging.getLogger(__name__)

DATA_KEY = f"{TYPE}.{DOMAIN}"


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
    cls_entities = {
        "default": AiotLightEntity
    }
    await manager.async_add_entities(
        config_entry, TYPE, cls_entities, async_add_entities
    )


class AiotLightEntity(AiotToggleableEntityBase, LightEntity):
    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotToggleableEntityBase.__init__(
            self, hass, device, res_params, TYPE, channel, **kwargs
        )
        self._attr_color_mode = kwargs.get("color_mode")
        if USE_KELVIN:
            self._attr_min_color_temp_kelvin = kwargs.get("min_color_temp_kelvin")
            self._attr_max_color_temp_kelvin = kwargs.get("max_color_temp_kelvin")
        else:
            min_k = kwargs.get("min_color_temp_kelvin")
            max_k = kwargs.get("max_color_temp_kelvin")
            self._attr_min_mireds = _kelvin_to_mireds(max_k) if max_k else None
            self._attr_max_mireds = _kelvin_to_mireds(min_k) if min_k else None
        self._extra_state_attributes.extend(["trigger_time", "trigger_dt", "color_mode"])

    async def async_turn_on(self, **kwargs):
        """Turn the specified light on."""
        hs_color = kwargs.get("hs_color")
        if hs_color:
            if self._attr_color_mode == "hs":
                await self.async_set_resource("color", hs_color)
            elif self._attr_color_mode == "xy":
                await self.async_set_resource("color", hs_color)

        brightness = kwargs.get("brightness")
        if brightness:
            await self.async_set_resource("brightness", brightness)

        color_temp_kelvin = kwargs.get("color_temp_kelvin")
        if color_temp_kelvin:
            await self.async_set_resource("color_temp", color_temp_kelvin)
        else:
            color_temp = kwargs.get("color_temp")
            if color_temp:
                # Legacy mireds path: convert to kelvin for resource handler
                await self.async_set_resource("color_temp", _mireds_to_kelvin(color_temp))

        await super().async_turn_on(**kwargs)

    def convert_attr_to_res(self, res_name, attr_value):
        if res_name == "brightness":
            # attr_value：0-255，亮度
            return int(attr_value * 100 / 255)
        elif res_name == "color" and self._attr_color_mode == "hs":
            # attr_value：hs颜色
            rgb_color = color_util.color_hs_to_RGB(*attr_value)
            return int(
                "{}{}{}{}".format(
                    hex(int(self.brightness * 100 / 255))[2:4].zfill(2),
                    hex(rgb_color[0])[2:4].zfill(2),
                    hex(rgb_color[1])[2:4].zfill(2),
                    hex(rgb_color[2])[2:4].zfill(2),
                ),
                16,
            )
        elif res_name == "color" and self._attr_color_mode == "xy":
            return
        elif res_name == "color_temp":
            # attr_value is kelvin, cloud expects mireds
            return _kelvin_to_mireds(attr_value)
        return super().convert_attr_to_res(res_name, attr_value)

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "brightness":
            # res_value：0-100，亮度百分比
            return int(int(res_value) * 255 / 100)
        elif res_name == "color" and self._attr_color_mode == "hs":
            # res_value：十进制整数字符串
            argb = hex(int(res_value))
            return color_util.color_RGB_to_hs(
                int(argb[4:6], 16), int(argb[6:8], 16), int(argb[8:10], 16)
            )
        elif res_name == "color" and self._attr_color_mode == "xy":
            return
        elif res_name == "color_temp":
            # res_value from cloud is mireds (153-500), convert to kelvin
            return _mireds_to_kelvin(int(res_value))
        return super().convert_res_to_attr(res_name, res_value)
