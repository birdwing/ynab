import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.sensor.const import SensorStateClass.TOTAL
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo

from custom_components.ynab.const import BUDGET_ICON, CONF_CURRENCY_KEY
from custom_components.ynab.api.data_coordinator import YnabDataCoordinator, DataCoordinatorModel

_LOGGER = logging.getLogger(__name__)

class BudgetSensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = STATE_CLASS_TOTAL
    _attr_has_entity_name = True
    _attr_icon = BUDGET_ICON

    def __init__(self, coordinator: YnabDataCoordinator, budget_id: str, budget_name: str, device_info: DeviceInfo):
        super().__init__(coordinator)

        self._attr_extra_state_attributes = {}
        self._attr_unique_id = f"budget_{budget_id}"
        self._attr_name = budget_name
        self._attr_device_info = device_info
        self._attr_native_unit_of_measurement = self.coordinator.data.currency_iso
        self._handle_data(coordinator.data)
        
    @callback
    def _handle_coordinator_update(self) -> None:
        self._handle_data(self.coordinator.data)
        self.async_write_ha_state()

    def _handle_data(self, data: DataCoordinatorModel):
        self._attr_native_value = data.to_be_budgeted

        # set attributes
        self._attr_extra_state_attributes["budgeted_this_month"] = data.budgeted_this_month
        self._attr_extra_state_attributes["activity_this_month"] = data.activity_this_month
        self._attr_extra_state_attributes["age_of_money"] = data.age_of_money
        self._attr_extra_state_attributes["total_balance"] = data.total_balance
        self._attr_extra_state_attributes["need_approval"] = data.need_approval
        self._attr_extra_state_attributes["uncleared_transactions"] = data.uncleared_transactions
        self._attr_extra_state_attributes["overspent_categories"] = data.overspent_categories
