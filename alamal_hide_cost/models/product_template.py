# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(groups="alamal_hide_cost.product_cost_group")
