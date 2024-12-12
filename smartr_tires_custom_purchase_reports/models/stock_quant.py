# -*- coding: utf-8 -*-
from odoo import models, fields


class StockQuant(models.Model):
    _inherit = "stock.quant"

    lot_source_id = fields.Many2one(related="lot_id.source_id", string="Lot Source", store=True, readonly=True)
    lot_year = fields.Char(related="lot_id.year", string="Lot Year", store=True, readonly=True)

    def _prepare_fast_sale_order_line(self, line, sales_order):
        values = super()._prepare_fast_sale_order_line(line, sales_order)

        values["lot_id"] = line.lot_id.id

        return values

    def _prepare_fast_purchase_order_line(self, line, purchase_order):
        values = super()._prepare_fast_purchase_order_line(line, purchase_order)

        values["lot_id"] = line.lot_id.id

        return values
