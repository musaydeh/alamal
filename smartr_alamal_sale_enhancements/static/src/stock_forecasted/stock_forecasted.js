/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { StockForecasted } from "@stock/stock_forecasted/stock_forecasted";
import { ForecastedLotFilter } from "./forecasted_lot_filter";
import { useState } from "@odoo/owl";

patch(StockForecasted, {
    components: {
        ...StockForecasted.components,
        ForecastedLotFilter,
    },
});

patch(StockForecasted.prototype, {
    setup() {
        super.setup();

         if(!this.context.warehouse_id) {
            this.context.warehouse_id = [];
         }

         this.lots = useState([]);

    },
    async _getReportValues() {
        await this._getResModel();
        const isTemplate = !this.resModel || this.resModel === 'product.template';
        this.reportModelName = `stock.forecasted_product_${isTemplate ? "template" : "product"}`;
        this.warehouses.splice(0, this.warehouses.length);
        this.warehouses.push(...await this.orm.searchRead('stock.warehouse', [],['id', 'name', 'code']));

        this.lots.splice(0, this.lots.length);

        const domain_lot = [];
        if (this.resModel === "product.template") {
            domain_lot.push(["product_id.product_tmpl_id", "=", this.productId]);
        } else if (this.resModel === "product.product") {
            domain_lot.push(["product_id", "=", this.productId]);
        }

        this.lots.push(...await this.orm.searchRead("stock.lot", domain_lot,["id", "name"]));

        if (!this.context.lot_id) {
           this.updateLot(this.lots[0].id);
        }

//        if (!this.context.warehouse_id) {
//            this.updateWarehouse(this.warehouses[0].id);
//        }
        const reportValues = await this.orm.call(this.reportModelName, "get_report_values", [], {
            context: this.context,
            docids: [this.productId],
        });
        this.docs = {
            ...reportValues.docs,
            ...reportValues.precision,
            lead_days_date: this.context.lead_days_date,
            qty_to_order: this.context.qty_to_order,
            visibility_days_date: this.context.visibility_days_date,
            qty_to_order_with_visibility_days: this.context.qty_to_order_with_visibility_days
        };
    },
    async updateWarehouse(id) {
        if(id == 0) {
            this.context.warehouse_id = [];
        } else {
            if(!this.context.warehouse_id) {
                this.context.warehouse_id = [];
            }

            const index = this.context.warehouse_id.indexOf(id);
            if(index == -1){
                this.context.warehouse_id.push(id);
            } else {
                this.context.warehouse_id.splice(index, 1);
            }
        }

        await this.reloadReport();

    },
    get graphDomain() {
        const domain = [["state", "=", "forecast"]]
        if(this.context.warehouse_id.length > 0) {
            domain.push(["warehouse_id", "in", this.context.warehouse_id]);
        } else {
            var warehouse_ids = [];
            for(let warehouse of this.warehouses){
                warehouse_ids.push(warehouse.id);
            }

            domain.push(["warehouse_id", "in", warehouse_ids]);
        }

        if (this.resModel === "product.template") {
            domain.push(["product_tmpl_id", "=", this.productId]);
        } else if (this.resModel === "product.product") {
            domain.push(["product_id", "=", this.productId]);
        }
        return domain;
    },
    async updateLot(id) {
        const hasPreviousValue = this.context.lot_id !== undefined;
        this.context.lot_id = id;
        if (hasPreviousValue) {
            await this.reloadReport();
        }
    }
});