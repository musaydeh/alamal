# coding: utf-8

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()

        res["lot_id"] = "l.lot_id"

        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,l.lot_id"""
        return res
