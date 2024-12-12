# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    type_ids = fields.Many2many("purchase.order.type", string="Types")
    total_discount = fields.Monetary(compute="_compute_total_discount", string="Total Discount", store=True,
                                     readonly=True)
    total_before_discount = fields.Monetary(compute="_compute_total_before_discount", string="Total before Discount",
                                            store=True, readonly=True)

    @api.depends("order_line.discount", "order_line.price_unit", "order_line.product_qty")
    def _compute_total_discount(self):
        for purchase_order in self:
            total_discount = 0
            for line in purchase_order.order_line.filtered(lambda l: not l.display_type):
                total_discount += (line.product_qty * (line.price_unit - line.price_unit_discounted))

            purchase_order.total_discount = total_discount

    @api.depends("amount_untaxed", "total_discount")
    def _compute_total_before_discount(self):
        for purchase_order in self:
            purchase_order.total_before_discount = purchase_order.amount_untaxed + purchase_order.total_discount

    @api.model
    def _get_picking_type(self, company_id):
        default_warehouse = self.env.user.with_company(company_id)._get_default_warehouse_id()
        if default_warehouse and default_warehouse.in_type_id:
            return default_warehouse.in_type_id

        return super()._get_picking_type(company_id)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def action_product_forecast_report(self):
        result = super().action_product_forecast_report()

        if result["context"]["warehouse_id"]:
            result["context"]["warehouse_id"] = [result["context"]["warehouse_id"]]

        return result
