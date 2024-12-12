# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _inherit = "product.product"

    total_value = fields.Monetary(groups="alamal_hide_cost.product_cost_group")
    avg_cost = fields.Monetary(groups="alamal_hide_cost.product_cost_group")
