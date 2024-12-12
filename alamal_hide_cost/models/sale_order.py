# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Monetary(groups="alamal_hide_cost.product_cost_group")
    margin_percent = fields.Float(groups="alamal_hide_cost.product_cost_group")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin = fields.Float(groups="alamal_hide_cost.product_cost_group")
    margin_percent = fields.Float(groups="alamal_hide_cost.product_cost_group")
    purchase_price = fields.Float(groups="alamal_hide_cost.product_cost_group")
