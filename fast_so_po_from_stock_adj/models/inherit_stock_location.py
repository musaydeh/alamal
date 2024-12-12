from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_temp_location = fields.Boolean()
