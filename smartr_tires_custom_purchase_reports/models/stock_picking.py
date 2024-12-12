# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    available_picking_type_ids = fields.Many2many("stock.picking.type", compute="_compute_available_picking_type_ids")
    picking_type_id = fields.Many2one(domain="[('id','in',available_picking_type_ids)]")

    @api.depends("sale_id")
    def _compute_available_picking_type_ids(self):
        stock_picking_type_obj = self.env["stock.picking.type"]

        for picking in self:
            if picking.sale_id:
                if picking.return_id:
                    domain = [("code", "=", "incoming")]
                else:
                    domain = [("code", "=", "outgoing")]

            elif picking.purchase_id:
                if picking.return_id:
                    domain = [("code", "=", "outgoing")]
                else:
                    domain = [("code", "=", "incoming")]
            else:
                domain = [("code", "in", ["incoming", "outgoing", "internal"])]

            picking.available_picking_type_ids = stock_picking_type_obj.search(domain)
