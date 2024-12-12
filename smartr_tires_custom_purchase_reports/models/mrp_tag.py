# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrderType(models.Model):
    _name = "mrp.tag"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "MRP Tag"

    name = fields.Char(string="Name", required=True, translate=True, index=True, tracking=True)
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
