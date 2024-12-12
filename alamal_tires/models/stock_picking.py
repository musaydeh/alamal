# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    location_id = fields.Many2one(domain=[('usage', '!=', 'view')])
    location_dest_id = fields.Many2one(domain=[('usage', '!=', 'view')])

    def action_detailed_operations(self):
        result = super().action_detailed_operations()

        if self.state in ["done", "cancel"]:
            result["context"].update({
                "create": False,
                "edit": False,
                "delete": False
            })

        return result
