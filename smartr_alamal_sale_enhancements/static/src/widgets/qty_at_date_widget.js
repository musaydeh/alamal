/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QtyAtDatePopover } from "@sale_stock/widgets/qty_at_date_widget";

patch(QtyAtDatePopover.prototype, {
    openForecast() {
        const warehouse_id =  this.props.record.data.warehouse_id && this.props.record.data.warehouse_id[0];
        const warehouse = warehouse_id && [warehouse_id] || [];

        this.actionService.doAction("stock.stock_forecasted_product_product_action", {
            additionalContext: {
                active_model: 'product.product',
                active_id: this.props.record.data.product_id[0],
                warehouse: warehouse,
                move_to_match_ids: this.props.record.data.move_ids.records.map(record => record.resId),
                sale_line_to_match_id: this.props.record.resId,
            },
        });
    }
});