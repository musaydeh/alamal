/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ForecastedWarehouseFilter } from "@stock/stock_forecasted/forecasted_warehouse_filter";


patch(ForecastedWarehouseFilter.prototype, {
    get activeWarehouses(){
        var activeWarehouses = "";

        if(this.context.warehouse_id.length > 0) {
            for(let warehouse of this.warehouses) {
                if(this.context.warehouse_id.indexOf(warehouse.id) != -1){
                    if(activeWarehouses) {
                        activeWarehouses += ",";
                    }
                    activeWarehouses += warehouse.name;
                }
            }
        } else {
            activeWarehouses = _t("All");
        }

        return activeWarehouses;
    },
    get warehousesItems() {
        var items = [{
            id: 0,
            label: _t("All"),
            class: { selected: this.context.warehouse_id.length <= 0},
            onSelected: () => this._onSelected(0),
        }].concat(this.warehouses.map(warehouse => ({
            id: warehouse.id,
            label: warehouse.name,
            class: { selected: this.context.warehouse_id.indexOf(warehouse.id) != -1 },
            onSelected: () => this._onSelected(warehouse.id),
        })));
        return items
    }
});