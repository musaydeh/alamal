# -*- coding: utf-8 -*-

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ["inter_warehouse_quant_id"]
        return fields

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
                               values):
        move_values = super()._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin,
                                                     company_id, values)

        move_dest_ids = values.get("move_dest_ids", False)
        if move_dest_ids and not values.get("inter_warehouse_quant_id", False):
            inter_warehouse_quant = move_dest_ids.inter_warehouse_quant_id
            if inter_warehouse_quant:
                move_values.update({
                    "inter_warehouse_quant_id": inter_warehouse_quant.id
                })

        return move_values
