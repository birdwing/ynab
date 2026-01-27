"""YNAB Integration."""
import logging
import os
from datetime import date, timedelta

from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import ConfigEntryNotReady
from ynab_sdk import YNAB

from .const import (
    CONF_BUDGET_KEY,
    CONF_CATEGORIES_KEY,
    CONF_ACCOUNTS_KEY,
    DEFAULT_API_ENDPOINT,
    DOMAIN,
    ISSUE_URL,
    REQUIRED_FILES,
    STARTUP,
    VERSION,
)
from .api.data_coordinator import YnabDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up this integration using config flow."""
    
    # 1. Initialize Domain Data
    hass.data.setdefault(DOMAIN, {})
    
    # startup message
    if entry.unique_id is None:
        # Only log startup once per unique ID generation if possible, but strict check is fine
        startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
        _LOGGER.info(startup)
    
    # 2. Setup Coordinator
    coordinator = YnabDataCoordinator(hass, entry.data)
    
    # 3. First Refresh
    await coordinator.async_config_entry_first_refresh()
    
    # 4. Store Coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # 5. Load Platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
