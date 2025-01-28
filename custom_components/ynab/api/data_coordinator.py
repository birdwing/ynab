import logging
import aiohttp
import json

from dataclasses import dataclass, field
from datetime import date, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY
from ynab_sdk import YNAB

from custom_components.ynab.const import (
    CONF_CURRENCY_KEY,
    CONF_BUDGET_KEY,
    CONF_CATEGORIES_KEY,
    CONF_CATEGORIES_ALL,
    CONF_ACCOUNTS_KEY,
    CONF_ACCOUNTS_ALL,
    DEFAULT_API_ENDPOINT,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class AccountModel:
    name: str
    balance: float

@dataclass
class CategoryModel:
    name: str
    balance: float
    budgeted: float
    activity: float
    goal_type: str
    goal_target: float
    goal_target_month: str
    goal_percentage_complete: int

@dataclass
class DataCoordinatorModel:
    to_be_budgeted: float
    total_balance: float
    budgeted_this_month: float
    activity_this_month: float

    age_of_money: int
    need_approval: int
    uncleared_transactions: int
    overspent_categories: int

    currency_iso: str

    accounts: dict[str, AccountModel] = field(default_factory=dict)
    categories: dict[str, CategoryModel] = field(default_factory=dict)

class YnabDataCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, config):
        super().__init__(hass, _LOGGER, name="YNAB", update_interval=timedelta(seconds=300))
        self.ynab = YNAB(config[CONF_API_KEY])
        self.api_key = config[CONF_API_KEY]
        self.budget = config[CONF_BUDGET_KEY]
        self.categories = config[CONF_CATEGORIES_KEY]
        self.categories_all = config[CONF_CATEGORIES_ALL]
        self.accounts = config[CONF_ACCOUNTS_KEY]
        self.accounts_all = config[CONF_ACCOUNTS_ALL]


    async def _async_update_data(self):
        """Update data."""

        # setup YNAB API
        await self.request_import()

        raw_budget = await self.hass.async_add_executor_job(
            self.ynab.budgets.get_budget, self.budget
        )

        get_data = raw_budget.data.budget
        _LOGGER.debug("Retrieving data from budget id: %s", get_data.id)

        # get to be budgeted data
        to_be_budgeted = (
            get_data.months[0].to_be_budgeted / 1000
        )
        _LOGGER.debug(
            "Received data for: to be budgeted: %s",
            (get_data.months[0].to_be_budgeted / 1000),
        )

        # get unapproved transactions
        unapproved_transactions = len(
            [
                transaction.amount
                for transaction in get_data.transactions
                if transaction.approved is not True
            ]
        )
        _LOGGER.debug(
            "Received data for: unapproved transactions: %s",
            unapproved_transactions,
        )

        # get number of uncleared transactions
        uncleared_transactions = len(
            [
                transaction.amount
                for transaction in get_data.transactions
                if transaction.cleared == "uncleared"
            ]
        )
        _LOGGER.debug(
            "Received data for: uncleared transactions: %s", uncleared_transactions
        )

        currency_iso = get_data.currency_format.iso_code

        total_balance = 0
        # get account data
        for account in get_data.accounts:
            if account.on_budget:
                total_balance += account.balance

        # get to be budgeted data
        _LOGGER.debug(
            "Received data for: total balance: %s",
            (total_balance / 1000),
        )

        # get accounts
        accounts: dict[str, AccountModel] = {}
        for account in get_data.accounts:
            if not self.accounts_all and account.id not in self.accounts:
                continue

            accounts.update([(account.id, AccountModel(account.name, account.balance / 1000))])
            _LOGGER.debug(
                "Received data for account: %s",
                [account.name, account.balance / 1000],
            )

        # get current month data
        for month in get_data.months:
            if month.month != date.today().strftime("%Y-%m-01"):
                continue

            # budgeted
            budgeted_this_month = month.budgeted / 1000
            _LOGGER.debug(
                "Received data for: budgeted this month: %s",
                budgeted_this_month,
            )

            # activity
            activity_this_month = month.activity / 1000
            _LOGGER.debug(
                "Received data for: activity this month: %s",
                activity_this_month,
            )

            # get age of money
            age_of_money = month.age_of_money
            _LOGGER.debug(
                "Received data for: age of money: %s",
                age_of_money,
            )

            # get number of overspend categories
            overspent_categories = len(
                [
                    category.balance
                    for category in month.categories
                    if category.balance < 0
                ]
            )
            _LOGGER.debug(
                "Received data for: overspent categories: %s",
                overspent_categories,
            )

            # get remaining category balances
            categories: dict[str, CategoryModel] = {}
            for category in month.categories:
                if not self.categories_all and category.id not in self.categories:
                    continue

                categories.update(
                    [(category.id, CategoryModel(category.name, category.balance / 1000,
                                                category.budgeted / 1000, category.activity / 1000,
                                                category.goal_type, category.goal_target / 1000,
                                                category.goal_target_month, category.goal_percentage_complete))]
                )
                
                _LOGGER.debug(
                    "Received data for categories: %s",
                    [category.name, category.balance / 1000, category.budgeted / 1000],
                )

            return DataCoordinatorModel(
                to_be_budgeted=to_be_budgeted,
                total_balance=total_balance / 1000,
                budgeted_this_month=budgeted_this_month,
                activity_this_month=activity_this_month,

                age_of_money=age_of_money,
                need_approval=unapproved_transactions,
                uncleared_transactions=uncleared_transactions,
                overspent_categories=overspent_categories,

                currency_iso=currency_iso,

                accounts=accounts,
                categories=categories,
            )

    async def request_import(self):
        """Force transaction import."""

        import_endpoint = (
            f"{DEFAULT_API_ENDPOINT}/budgets/{self.budget}/transactions/import"
        )
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url=import_endpoint) as response:
                    if response.status in [200, 201]:
                        response_data = json.loads(await response.text())

                        _LOGGER.debug(
                            "Imported transactions: %s",
                            len(response_data["data"]["transaction_ids"]),
                        )
                        _LOGGER.debug("API Stats: %s", response.headers["X-Rate-Limit"])

                        if len(response_data["data"]["transaction_ids"]) > 0:
                            _event_topic = DOMAIN + "_event"
                            _event_data = {
                                "transactions_imported": len(
                                    response_data["data"]["transaction_ids"]
                                )
                            }
                            self.hass.bus.async_fire(_event_topic, _event_data)

        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.debug("Error encounted during forced import - %s", error)