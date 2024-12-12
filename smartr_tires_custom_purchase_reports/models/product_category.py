# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLot(models.Model):
    _inherit = "product.category"

    is_tire = fields.Boolean(string="Tire")
