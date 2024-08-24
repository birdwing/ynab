"""YNAB Integration."""

import json
import logging
import os
from datetime import date, timedelta

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
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

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up this integration using config flow."""
    # startup message
    startup = STARTUP.format(name=DOMAIN, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(startup)

    # check all required files
    file_check = await check_files(hass)
    if not file_check:
        return False

    url_check = await check_url()
    if not url_check:
        return False

    # get global config
    budget = entry.data[CONF_BUDGET_KEY]
    _LOGGER.debug("YAML configured budget - %s", budget)

    if CONF_CATEGORIES_KEY in entry.data:
        categories = entry.data[CONF_CATEGORIES_KEY]
        _LOGGER.debug("Monitoring categories - %s", categories)

    if CONF_ACCOUNTS_KEY in entry.data:
        accounts = entry.data[CONF_ACCOUNTS_KEY]
        _LOGGER.debug("Monitoring accounts - %s", accounts)

    hass.data[DOMAIN_DATA]["client"] = YnabData(hass, entry)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True

async def check_files(hass):
    """Return bool that indicates if all files are present."""
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = f"{base}{file}"
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def check_url():
    """Return bool that indicates YNAB URL is accessible."""

    url = DEFAULT_API_ENDPOINT

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    _LOGGER.debug("Connection with YNAB established")
                    result = True
                else:
                    _LOGGER.debug(
                        "Connection with YNAB established, "
                        "but wasnt able to communicate with API endpoint"
                    )
                    result = False
    except Exception as error:  # pylint: disable=broad-except
        _LOGGER.debug("Unable to establish connection with YNAB - %s", error)
        result = False

    return result