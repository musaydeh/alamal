# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("journal_id")
    def _compute_fiscal_position_id(self):
        super()._compute_fiscal_position_id()

        for move in self.filtered(lambda m: m.journal_id.fiscal_position_id):
            move.fiscal_position_id = move.journal_id.fiscal_position_id
