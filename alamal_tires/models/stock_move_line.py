# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    overall_moving_balance = fields.Float(sting="Over All Moving Balance", digits="Product Unit of Measure", copy=False,
                                          readonly=False)
    order_responsible_id = fields.Many2one("res.users", compute="_compute_order_responsible",
                                           string="Order Responsible", readonly=True, store=True)

    @api.depends("move_id.group_id.responsible_id")
    def _compute_order_responsible(self):
        for move_line in self:
            move_line.order_responsible_id = move_line.move_id.group_id.responsible_id

    def _action_done(self):
        super()._action_done()

        for move_line in self:
            move_line.product_id._compute_quantities()
            move_line.write({"overall_moving_balance": move_line.product_id.qty_available})
