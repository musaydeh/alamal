# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_branch_company_ids = fields.Many2many("res.company", string="Allowed Branch Companies",
                                                  domain=[("is_main_company", "=", False)])
