from odoo import api, fields, models

class Container(models.Model):
    _name = 'sale.container'

    name = fields.Char()
