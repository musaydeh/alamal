# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    type_ids = fields.Many2many("purchase.order.type", string="Types")


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    product_tracking = fields.Selection(related='product_id.tracking', depends=['product_id'])
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number", check_company=True)

    @api.onchange("type_ids")
    def onchange_purchase_types(self):
        if self.type_ids:
            for line in self.order_line.filtered(lambda l: l.lot_id):
                if line.lot_id.source_id not in self.type_ids._origin:
                    line.lot_id = False

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        values = super()._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)

        if self.lot_id:
            values.update({"lot_id": self.lot_id.id})

        return values
