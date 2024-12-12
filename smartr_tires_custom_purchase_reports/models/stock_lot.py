# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = "stock.lot"

    product_kind = fields.Selection(related="product_id.product_kind")
    product_tire_brand = fields.Many2one(related="product_id.tire_brand", string="Brand", readonly=True, store=True)
    product_tire_pattern = fields.Many2one(related="product_id.tire_brand", string="Pattern", readonly=True, store=True)
    source_id = fields.Many2one("purchase.order.type", string="Source")
    year = fields.Char(string="Year")

    @api.onchange("source", "year")
    def onchange_source_and_year(self):
        ref = ""
        if self.source_id.code and self.year:
            ref = f"{self.source_id.code}-{self.year}"

        self.ref = ref

    @api.onchange("product_id", "source_id", "year")
    def onchange_product(self):
        if self.product_id and self.product_id.product_kind == "tire":
            if self.source_id.code and self.year:
                self.name = f"{self.source_id.code}-{self.year}"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        lots = self.search_fetch(args + ['|', '|', ('name', operator, name), ('product_id.name', operator, name),
                                         ('product_id.second_name', operator, name)],
                                 ["display_name"], limit=limit)
        return [(lot.id, lot.display_name) for lot in lots.sudo()]
