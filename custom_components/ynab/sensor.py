"""Sensor platform for ynab."""
import logging
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .const import (ACCOUNT_ERROR, CATEGORY_ERROR,
                    DOMAIN, CONF_ACCOUNTS_KEY,
                    CONF_BUDGET_KEY, CONF_CATEGORIES_KEY,
                    CONF_BUDGET_NAME_KEY)

from .sensors.balance_sensor import CategorySensor, AccountSensor
from .sensors.budget_sensor import BudgetSensor
from .api.data_coordinator import YnabDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, config_entry, async_add_entities
):
    """Set up sensor platform."""
    _LOGGER.debug("Setting up entities")
    
    coordinator = YnabDataCoordinator(hass, config_entry.data)
    await coordinator.async_config_entry_first_refresh()

    budget_id = config_entry.data[CONF_BUDGET_KEY]
    budget_name = config_entry.data[CONF_BUDGET_NAME_KEY]
    device_info = DeviceInfo(
        name=budget_name,
        manufacturer=DOMAIN,
        model="Budget",
        via_device=(DOMAIN, budget_id),
        identifiers={(DOMAIN, budget_id)}
    )
    
    sensors = [BudgetSensor(coordinator, budget_id, budget_name, device_info)]
    
    categories = []
    if CONF_CATEGORIES_KEY in config_entry.data:
        categories = config_entry.data[CONF_CATEGORIES_KEY]

    for category in categories:
        sensors.append(CategorySensor(coordinator, category_id=category, device_info=device_info, budget_name=budget_name))

    accounts = []
    if CONF_ACCOUNTS_KEY in config_entry.data:
        accounts = config_entry.data[CONF_ACCOUNTS_KEY]

    for account in accounts:
        sensors.append(AccountSensor(coordinator, account_id=account, device_info=device_info, budget_name=budget_name))

    async_add_entities(sensors, update_before_add=True)