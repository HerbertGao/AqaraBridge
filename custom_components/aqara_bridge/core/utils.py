""" the Aqara Bridge utils."""
from datetime import datetime

from homeassistant.core import HomeAssistant

try:
    from homeassistant.util.dt import get_default_time_zone
except ImportError:
    from homeassistant.util.dt import DEFAULT_TIME_ZONE
    get_default_time_zone = lambda: DEFAULT_TIME_ZONE

try:
    from homeassistant.util.dt import async_get_time_zone
except ImportError:
    from homeassistant.util.dt import get_time_zone as async_get_time_zone

def local_zone(hass=None):
    try:
        if isinstance(hass, HomeAssistant):
            return async_get_time_zone(hass.config.time_zone)
        return get_default_time_zone()
    except KeyError:
        pass
    return get_default_time_zone()

def ts_format_str_ms(str_timestamp_ms : str,hass=None):
    if str_timestamp_ms:
        timestamp = round(int(str_timestamp_ms)/1000,0)
        return datetime.fromtimestamp(timestamp, local_zone(hass))

def ts_format_str_s(str_timestamp_s : str,hass=None):
    if str_timestamp_s:
        timestamp = int(str_timestamp_s)
        return datetime.fromtimestamp(timestamp, local_zone(hass))
