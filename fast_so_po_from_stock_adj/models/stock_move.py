# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    inter_warehouse_quant_id = fields.Many2one("stock.quant", string="Inter-Warehouse Quant", readonly=True, copy=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append("inter_warehouse_quant_id")
        return distinct_fields
