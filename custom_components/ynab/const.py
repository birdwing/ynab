"""Constants for YNAB integration."""
DOMAIN = "ynab"
DOMAIN_DATA = f"{DOMAIN}_data"

REQUIRED_FILES = ["const.py", "manifest.json", "sensor.py"]
VERSION = "0.4.0"
ISSUE_URL = "https://github.com/birdwing/ynab/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

DEFAULT_NAME = "ynab"
DEFAULT_BUDGET = "last-used"
DEFAULT_CURRENCY = "$"
DEFAULT_API_ENDPOINT = "https://api.ynab.com/v1"

BUDGET_ICON = "mdi:finance"
CATEGORY_ICON = "mdi:cash"
ACCOUNT_ICON = "mdi:bank-circle-outline"

CONF_NAME = "name"
CONF_ENABLED = "enabled"
CONF_SENSOR = "sensor"

CONF_BUDGET_KEY = "budget"
CONF_BUDGET_NAME_KEY = "budget_name"
CONF_CATEGORIES_KEY = "categories"
CONF_ACCOUNTS_KEY = "accounts"
CONF_CURRENCY_KEY = "currency"