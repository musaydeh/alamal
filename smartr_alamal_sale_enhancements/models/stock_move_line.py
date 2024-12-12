# -*- coding: utf-8 -*-

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_id = fields.Many2one(readonly=True)
