import logging
import re
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode

from .core.aiot_manager import (
    AiotManager,
    AiotEntityBase,
)
from .core.aiot_mapping import SPECIAL_DEVICES_INFO
from .core.const import DOMAIN, HASS_DATA_AIOT_MANAGER

TYPE = "climate"

_LOGGER = logging.getLogger(__name__)

DATA_KEY = f"{TYPE}.{DOMAIN}"


AC_STATE_MAPPING = {
    "hvac_mode": {
        "off": [{"code": "0000", "start": 0, "end": 4}],
        "heat": [
            {"code": "0001", "start": 0, "end": 4},
            {"code": "0000", "start": 4, "end": 8},
        ],
        "cool": [
            {"code": "0001", "start": 0, "end": 4},
            {"code": "0001", "start": 4, "end": 8},
        ],
    },
    "fan_mode": {
        "low": [{"code": "0000", "start": 8, "end": 12}],
        "middle": [{"code": "0001", "start": 8, "end": 12}],
        "high": [{"code": "0010", "start": 8, "end": 12}],
    },
    "temperature": {"0": [{"start": 16, "end": 24}]},
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
    cls_entities = {
        "climate": AiotAcCompanionEntity,
        "default": AiotClimateEntity
    }
    await manager.async_add_entities(
        config_entry, TYPE, cls_entities, async_add_entities
    )


class AiotClimateEntity(AiotEntityBase, ClimateEntity):
    """VRF空调控制器，特殊资源定义"""

    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        self._attr_hvac_modes = kwargs.get("hvac_modes")
        self._attr_temperature_unit = kwargs.get("unit_of_measurement")
        self._attr_target_temperature_step = kwargs.get("target_temp_step")
        self._attr_fan_modes = kwargs.get("fan_modes")
        self._attr_min_temp = kwargs.get("min_temp")
        self._attr_max_temp = kwargs.get("max_temp")
        self._state_str = "".zfill(32)

    async def _async_change_ac_state(self, attr_name, attr_value, fix_code=None):
        mappings = AC_STATE_MAPPING[attr_name].get(attr_value)
        new_state_str = self._state_str
        if mappings:
            for mapping in mappings:
                code = fix_code if fix_code else mapping["code"]
                start = mapping["start"]
                end = mapping["end"]
                new_state_str = f"{new_state_str[0:start]}{code}{new_state_str[end:]}"

            await self.async_set_resource("ac_state", new_state_str)
        else:
            _LOGGER.warning(f"Attr value '{attr_value}' is not supported in {attr_name}")

    async def async_set_fan_mode(self, fan_mode: str):
        await self._async_change_ac_state("fan_mode", fan_mode)

    async def async_set_hvac_mode(self, hvac_mode: str):
        await self._async_change_ac_state("hvac_mode", hvac_mode)

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        await self._async_change_ac_state(
            "temperature", "0", bin(int(temperature))[2:].zfill(8)
        )

    def convert_attr_to_res(self, res_name, value):
        if res_name == "ac_state":
            # res_value：二进制字符串
            return int(value, 2)
        return super().convert_attr_to_res(res_name, value)

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "ac_state":
            # res_value: 十进制字符串
            return bin(int(res_value))[2:].zfill(32)
        return super().convert_res_to_attr(res_name, res_value)

    def __setattr__(self, name: str, value):
        if name == "_state_str" and value != "".zfill(32):
            sdi = SPECIAL_DEVICES_INFO[self._device.model]
            self._attr_hvac_mode = sdi["hvac_mode"][int(value[4:8], 2)]
            if int(value[0:4], 2) == 0:
                self._attr_hvac_mode = "off"
            self._attr_fan_mode = sdi["fan_mode"][int(value[8:12], 2)]
            self._attr_target_temperature = int(value[16:24], 2)
        return super().__setattr__(name, value)


# ac_zip_status bit field mapping (for acn05)
# P[31:28]=power(0=on,1=off) M[27:24]=mode S[23:20]=fan D[17:16]=swing T[15:8]=temp
_ZIP_MODES = {0: HVACMode.HEAT, 1: HVACMode.COOL, 2: HVACMode.AUTO, 3: HVACMode.DRY, 4: HVACMode.FAN_ONLY}
_ZIP_MODES_REV = {v: k for k, v in _ZIP_MODES.items()}
_ZIP_FANS = {0: "low", 1: "medium", 2: "high", 3: "auto"}
_ZIP_FANS_REV = {v: k for k, v in _ZIP_FANS.items()}

# send_ac_cmd P3 format mapping
# P=power(0=on,1=off) M=mode(0=cool,1=heat,2=auto,3=fan,4=dry)
_CMD_MODES = {0: HVACMode.COOL, 1: HVACMode.HEAT, 2: HVACMode.AUTO, 3: HVACMode.FAN_ONLY, 4: HVACMode.DRY}
_CMD_MODES_REV = {v: k for k, v in _CMD_MODES.items()}
_CMD_FANS = {0: "auto", 1: "low", 2: "medium", 3: "high"}
_CMD_FANS_REV = {v: k for k, v in _CMD_FANS.items()}


def _parse_ac_zip(value: int):
    """Parse ac_zip_status bit fields."""
    power = (value >> 28) & 0xF
    mode = (value >> 24) & 0xF
    fan = (value >> 20) & 0xF
    swing = (value >> 16) & 0x3
    temp = (value >> 8) & 0xFF
    return power, mode, fan, swing, temp


def _build_ac_cmd(power, mode, temp, fan, swing):
    """Build send_ac_cmd P3 format string."""
    return f"P{power}_M{mode}_T{temp}_S{fan}_D{swing}"


class AiotAcCompanionEntity(AiotEntityBase, ClimateEntity):
    """Aqara Air Conditioning Companion (acn05) using send_ac_cmd P3 format."""

    def __init__(self, hass, device, res_params, channel=None, **kwargs):
        AiotEntityBase.__init__(self, hass, device, res_params, TYPE, channel, **kwargs)
        # Re-set after AiotEntityBase.__init__ overrides class attr with kwargs.get()
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.SWING_MODE
        )
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.AUTO, HVACMode.DRY, HVACMode.FAN_ONLY]
        self._attr_fan_modes = ["auto", "low", "medium", "high"]
        self._attr_swing_modes = ["on", "off"]
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._attr_temperature_unit = kwargs.get("unit_of_measurement", "°C")
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_fan_mode = "auto"
        self._attr_swing_mode = "off"
        self._attr_target_temperature = 26
        self._attr_current_temperature = None
        # Track current state for building commands
        self._power = 1  # off
        self._mode = 0
        self._fan = 0
        self._swing = 1  # fixed

    async def _send_cmd(self):
        """Send P3 format command."""
        cmd = _build_ac_cmd(self._power, self._mode, int(self._attr_target_temperature), self._fan, self._swing)
        await self.async_set_resource("send_ac_cmd", cmd)

    async def async_set_hvac_mode(self, hvac_mode: str):
        if hvac_mode == HVACMode.OFF:
            self._power = 1
        else:
            self._power = 0
            self._mode = _CMD_MODES_REV.get(hvac_mode, 0)
        await self._send_cmd()

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get("temperature")
        if temp is not None:
            self._attr_target_temperature = int(temp)
        await self._send_cmd()

    async def async_set_fan_mode(self, fan_mode: str):
        self._fan = _CMD_FANS_REV.get(fan_mode, 0)
        await self._send_cmd()

    async def async_set_swing_mode(self, swing_mode: str):
        self._swing = 0 if swing_mode == "on" else 1
        await self._send_cmd()

    def convert_attr_to_res(self, res_name, attr_value):
        if res_name == "send_ac_cmd":
            return str(attr_value)
        return super().convert_attr_to_res(res_name, attr_value)

    def convert_res_to_attr(self, res_name, res_value):
        if res_name == "ac_zip_status":
            # Parse bit fields to update state
            value = int(res_value)
            power, mode, fan, swing, temp = _parse_ac_zip(value)
            self._power = power
            self._mode = mode
            self._fan = fan
            self._swing = swing
            if power == 0:
                self._attr_hvac_mode = _ZIP_MODES.get(mode, HVACMode.OFF)
            else:
                self._attr_hvac_mode = HVACMode.OFF
            self._attr_fan_mode = _ZIP_FANS.get(fan, "auto")
            self._attr_swing_mode = "on" if swing == 0 else "off"
            if temp != 255 and temp != 243 and temp != 244:
                self._attr_target_temperature = temp
            return value
        if res_name == "on_off_status":
            is_on = int(res_value) == 1
            if not is_on:
                self._attr_hvac_mode = HVACMode.OFF
                self._power = 1
            return int(res_value)
        if res_name == "temperature_value":
            # Unit: 0.01°C
            return round(int(res_value) / 100.0, 1)
        if res_name == "send_ac_cmd":
            # Parse P3 format: P0_M0_T26_S0_D0
            m = re.match(r'P(\d+)_M(\d+)_T(\d+)_S(\d+)_D(\d+)', str(res_value))
            if m:
                p, mode, temp, fan, swing = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
                self._power = p
                self._mode = mode
                self._fan = fan
                self._swing = swing
                if p == 0:
                    self._attr_hvac_mode = _CMD_MODES.get(mode, HVACMode.OFF)
                else:
                    self._attr_hvac_mode = HVACMode.OFF
                self._attr_fan_mode = _CMD_FANS.get(fan, "auto")
                self._attr_swing_mode = "on" if swing == 0 else "off"
                self._attr_target_temperature = temp
            return str(res_value)
        return super().convert_res_to_attr(res_name, res_value)

    def __setattr__(self, name: str, value):
        if name == "_attr_current_temperature" and value is not None:
            pass  # Allow direct assignment
        return super().__setattr__(name, value)
