from odoo import api, fields, models


class ResUser(models.Model):
    _inherit = 'res.users'

    last_created_sale_order = fields.Many2one(comodel_name="sale.order", string="Last Sale Order")
