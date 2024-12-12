from odoo import api, fields, models

class FiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    is_export = fields.Boolean(string="",  )