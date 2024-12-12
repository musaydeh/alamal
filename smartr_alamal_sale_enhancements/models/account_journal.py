# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position", check_company=True)
