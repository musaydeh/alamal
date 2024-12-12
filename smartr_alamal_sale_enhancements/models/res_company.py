# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    is_main_company = fields.Boolean(string="Is Main Company")
