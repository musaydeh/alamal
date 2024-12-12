# -*- coding: utf-8 -*-

from odoo import models, fields


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    print_from_procurement_group = fields.Boolean(sting="Print from Procurement Group")
