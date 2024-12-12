# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number", readonly=True)

    def _select(self) -> SQL:
        return SQL(
            """
                %s,
                l.lot_id as lot_id
            """, super()._select()
        )

    def _group_by(self) -> SQL:
        return SQL("%s, l.lot_id", super()._group_by())
