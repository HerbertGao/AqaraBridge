import datetime
import re
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.storage import Store

from .core.aiot_manager import (
    AiotManager,
    AiotDevice,
)
from .core.aiot_cloud import AiotCloud
from .core.const import *

STORAGE_KEY = "aqara_bridge.tokens"
STORAGE_VERSION = 1
REFRESH_RETRY_DELAY = 1800  # 30 minutes
REFRESH_BEFORE_EXPIRY = 3600  # 1 hour before expiry


_LOGGER = logging.getLogger(__name__)

_DEBUG_ACCESSTOKEN = ""
_DEBUG_REFRESH_TOKEN = ""
_DEBUG_STATUS = False


def data_masking(s: str, n: int) -> str:
    return re.sub(f"(?<=.{{{n}}}).(?=.{{{n}}})", "*", str(s))


def gen_auth_entry(
    app_id: str, app_key: str, key_id: str, 
    account: str, account_type: int, country_code: str, 
    token_result: dict
):
    auth_entry = {}
    auth_entry[CONF_ENTRY_APP_ID] = app_id
    auth_entry[CONF_ENTRY_APP_KEY] = app_key
    auth_entry[CONF_ENTRY_KEY_ID] = key_id
    auth_entry[CONF_ENTRY_AUTH_ACCOUNT] = account
    auth_entry[CONF_ENTRY_AUTH_ACCOUNT_TYPE] = account_type
    auth_entry[CONF_ENTRY_AUTH_COUNTRY_CODE] = country_code
    auth_entry[CONF_ENTRY_AUTH_OPENID] = token_result["openId"]
    auth_entry[CONF_ENTRY_AUTH_ACCESS_TOKEN] = token_result["accessToken"]
    auth_entry[CONF_ENTRY_AUTH_EXPIRES_IN] = token_result["expiresIn"]
    auth_entry[CONF_ENTRY_AUTH_EXPIRES_TIME] = (
        datetime.datetime.now()
        + datetime.timedelta(seconds=int(token_result["expiresIn"]))
    ).strftime("%Y-%m-%d %H:%M:%S")
    auth_entry[CONF_ENTRY_AUTH_REFRESH_TOKEN] = token_result["refreshToken"]
    return auth_entry


def init_hass_data(hass):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(HASS_DATA_AUTH_ENTRY_ID, None)
    session = AiotCloud(aiohttp_client.async_create_clientsession(hass))
    if not hass.data[DOMAIN].get(HASS_DATA_AIOTCLOUD):
        hass.data[DOMAIN].setdefault(HASS_DATA_AIOTCLOUD, session)
    if not hass.data[DOMAIN].get(HASS_DATA_AIOT_MANAGER):
        hass.data[DOMAIN].setdefault(HASS_DATA_AIOT_MANAGER, AiotManager(hass, session))

async def async_setup(hass, config):
    """Setup component."""
    init_hass_data(hass)
    return True


async def _notify_user(hass, message):
    """Send a persistent notification to the user."""
    await hass.services.async_call(
        "persistent_notification", "create",
        {"message": message, "title": "Aqara Bridge"},
    )


def _apply_refresh_result(hass, entry, data, resp_result):
    """Update config entry with refreshed token and return refresh delay."""
    auth_entry = gen_auth_entry(
        data.get(CONF_ENTRY_APP_ID),
        data.get(CONF_ENTRY_APP_KEY),
        data.get(CONF_ENTRY_KEY_ID),
        data.get(CONF_ENTRY_AUTH_ACCOUNT),
        data.get(CONF_ENTRY_AUTH_ACCOUNT_TYPE),
        data.get(CONF_ENTRY_AUTH_COUNTRY_CODE),
        resp_result,
    )
    hass.config_entries.async_update_entry(entry, data=auth_entry)
    return max(int(resp_result["expiresIn"]) - REFRESH_BEFORE_EXPIRY, REFRESH_BEFORE_EXPIRY)


def _save_tokens_to_store(hass, access_token, refresh_token):
    """Persist tokens to Store."""
    store = hass.data[DOMAIN].get(HASS_DATA_TOKEN_STORE)
    if store:
        hass.async_create_task(store.async_save({
            "access_token": access_token,
            "refresh_token": refresh_token,
        }))


def _schedule_token_refresh(hass, entry, delay):
    """Schedule a token refresh after delay seconds."""
    # Cancel existing timer if any
    old_timer = hass.data[DOMAIN].get(HASS_DATA_REFRESH_TIMER)
    if old_timer is not None:
        old_timer.cancel()

    handle = hass.loop.call_later(
        delay,
        lambda: hass.async_create_task(
            _async_do_refresh(hass, entry)
        ),
    )
    hass.data[DOMAIN][HASS_DATA_REFRESH_TIMER] = handle
    _LOGGER.debug(f"Token refresh scheduled in {delay}s")


async def _async_do_refresh(hass, entry):
    """Perform token refresh and schedule next one."""
    aiotcloud: AiotCloud = hass.data[DOMAIN][HASS_DATA_AIOTCLOUD]

    try:
        resp = await aiotcloud.async_refresh_token(aiotcloud.refresh_token)
        if isinstance(resp, dict) and resp["code"] == 0:
            delay = _apply_refresh_result(hass, entry, entry.data.copy(), resp["result"])
        else:
            _LOGGER.error(f"Token refresh failed: {resp}")
            await _notify_user(hass, "Aqara token refresh failed. Please re-authorize.")
            delay = REFRESH_RETRY_DELAY
    except Exception as ex:
        _LOGGER.error(f"Token refresh error: {ex}")
        await _notify_user(hass, f"Aqara token refresh error: {ex}")
        delay = REFRESH_RETRY_DELAY

    _schedule_token_refresh(hass, entry, delay)


async def async_setup_entry(hass, entry):
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    def token_updated(access_token, refresh_token):
        auth_entry = hass.data[DOMAIN][HASS_DATA_AUTH_ENTRY_ID]
        if auth_entry:
            data = auth_entry.data.copy()
            data[CONF_ENTRY_AUTH_ACCESS_TOKEN] = access_token
            data[CONF_ENTRY_AUTH_REFRESH_TOKEN] = refresh_token
            hass.config_entries.async_update_entry(entry, data=data)
        _save_tokens_to_store(hass, access_token, refresh_token)

    # add update handler
    if not entry.update_listeners:
        entry.add_update_listener(async_update_options)

    data = entry.data.copy()
    if _DEBUG_STATUS:
        import time
        data[CONF_ENTRY_AUTH_REFRESH_TOKEN] = _DEBUG_REFRESH_TOKEN
        data[CONF_ENTRY_AUTH_ACCESS_TOKEN] = _DEBUG_ACCESSTOKEN
        data[CONF_ENTRY_AUTH_EXPIRES_TIME] = time.strftime("%Y-%m-%d %H:%M:%S",
            time.localtime(time.time() + 24 * 3600))

    # Try to load tokens from Store (survives restarts better than config_entry)
    stored_tokens = await store.async_load()
    if stored_tokens:
        if stored_tokens.get("access_token"):
            data[CONF_ENTRY_AUTH_ACCESS_TOKEN] = stored_tokens["access_token"]
        if stored_tokens.get("refresh_token"):
            data[CONF_ENTRY_AUTH_REFRESH_TOKEN] = stored_tokens["refresh_token"]

    manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
    aiotcloud: AiotCloud = hass.data[DOMAIN][HASS_DATA_AIOTCLOUD]
    aiotcloud.set_options(entry.options)
    aiotcloud.set_app_id(data[CONF_ENTRY_APP_ID])
    aiotcloud.set_app_key(data[CONF_ENTRY_APP_KEY])
    aiotcloud.set_key_id(data[CONF_ENTRY_KEY_ID])
    aiotcloud.update_token_event_callback = token_updated
    hass.data[DOMAIN][HASS_DATA_TOKEN_STORE] = store
    if manager._msg_handler is not None:
        # 如果重新配置，重新启动mq
        manager._msg_handler.stop()
    manager.start_msg_hanlder(data[CONF_ENTRY_APP_ID], data[CONF_ENTRY_APP_KEY], data[CONF_ENTRY_KEY_ID])

    expires_time = datetime.datetime.strptime(
        data.get(CONF_ENTRY_AUTH_EXPIRES_TIME), "%Y-%m-%d %H:%M:%S"
    )
    if expires_time <= datetime.datetime.now():
        # Token expired, refresh immediately
        resp = await aiotcloud.async_refresh_token(
            data.get(CONF_ENTRY_AUTH_REFRESH_TOKEN)
        )
        if isinstance(resp, dict) and resp["code"] == 0:
            refresh_delay = _apply_refresh_result(hass, entry, data, resp["result"])
        else:
            _LOGGER.error(f"Token refresh failed at startup: {resp}")
            await _notify_user(hass, "Aqara token expired and refresh failed. Please re-authorize.")
            return False
    else:
        aiotcloud.set_country(data.get(CONF_ENTRY_AUTH_COUNTRY_CODE))
        aiotcloud.access_token = data.get(CONF_ENTRY_AUTH_ACCESS_TOKEN)
        aiotcloud.refresh_token = data.get(CONF_ENTRY_AUTH_REFRESH_TOKEN)
        # Compute delay until refresh is needed
        remaining = (expires_time - datetime.datetime.now()).total_seconds()
        refresh_delay = max(remaining - REFRESH_BEFORE_EXPIRY, REFRESH_BEFORE_EXPIRY)

    hass.data[DOMAIN][HASS_DATA_AUTH_ENTRY_ID] = entry
    if len(manager.all_devices) == 0:
        await manager.async_add_all_devices(entry)
        await manager.async_forward_entry_setup(entry)
    else:
        await manager.async_add_all_devices(entry)

    # Schedule proactive token refresh (no immediate refresh if token is fresh)
    _schedule_token_refresh(hass, entry, refresh_delay)

    return True


async def async_unload_entry(hass, entry):
    # Cancel proactive token refresh timer
    timer = hass.data[DOMAIN].get(HASS_DATA_REFRESH_TIMER)
    if timer is not None:
        timer.cancel()
        hass.data[DOMAIN].pop(HASS_DATA_REFRESH_TIMER, None)
    return True


async def async_remove_entry(hass, entry):
    if CONF_ENTRY_AUTH_ACCOUNT in entry.data:
        hass.data[DOMAIN][HASS_DATA_AUTH_ENTRY_ID] = None
    else:
        manager: AiotManager = hass.data[DOMAIN][HASS_DATA_AIOT_MANAGER]
        await manager.async_remove_entry(entry)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """ Update Optioins if available """
    await hass.config_entries.async_reload(entry.entry_id)
