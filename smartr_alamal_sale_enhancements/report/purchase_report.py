# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    qty_to_receive = fields.Float('Qty to Receive', readonly=True)

    def _select(self) -> SQL:
        return SQL(
            """
                %s,
                sum((l.product_qty - l.qty_received) / line_uom.factor * product_uom.factor) as qty_to_receive
            """, super()._select()
        )
