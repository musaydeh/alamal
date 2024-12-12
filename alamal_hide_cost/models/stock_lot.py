# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLot(models.Model):
    _inherit = "stock.lot"

    total_value = fields.Monetary(groups="alamal_hide_cost.product_cost_group")
    avg_cost = fields.Monetary(groups="alamal_hide_cost.product_cost_group")
    standard_price = fields.Float(groups="alamal_hide_cost.product_cost_group")
