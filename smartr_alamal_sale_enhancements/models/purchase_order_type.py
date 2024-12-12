# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Purchase Order Type"

    name = fields.Char(string="Name", required=True, translate=True, index=True, tracking=True)
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
