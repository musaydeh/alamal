# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductOESpecification(models.Model):
    _name = "product.oe.specification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product OE Specification"

    name = fields.Char(string="Name", required=True, translate=True, index=True, tracking=True)
    description = fields.Text(string="Description")
