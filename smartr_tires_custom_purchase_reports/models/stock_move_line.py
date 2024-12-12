# -*- coding: utf-8 -*-

from odoo import models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals):
        res = super().create(vals)

        if res.move_id.state not in ["cancel", "done"]:
            if res.move_id.sale_line_id:
                lot = res.move_id.sale_line_id.lot_id
                if lot:
                    res.write({"lot_id": lot.id})
            elif res.move_id.purchase_line_id:
                lot = res.move_id.purchase_line_id.lot_id
                if lot:
                    res.write({"lot_id": lot.id})

        return res
