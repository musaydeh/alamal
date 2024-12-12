# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_sale_journal_id = fields.Many2one("account.journal", company_dependent=True, string="Invoicing Journal",
                                               domain="[('type', '=', 'sale')]", ondelete="restrict")
    property_purchase_journal_id = fields.Many2one("account.journal", company_dependent=True, string="Billing Journal",
                                                   domain="[('type', '=', 'purchase')]", ondelete="restrict")
