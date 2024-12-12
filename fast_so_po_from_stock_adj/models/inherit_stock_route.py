from odoo import api, fields, models


class StockRoute(models.Model):
    _inherit = 'stock.route'

    deliver_from_warehouse = fields.Many2one(comodel_name="stock.warehouse", string="", required=False)
    inter_warehouse_transfer = fields.Boolean(string="Inter-Warehouse Transfer")

    _sql_constraints = [
        ('deliver_from_warehouse_unique', 'unique(deliver_from_warehouse)', 'Deliver From WH must be unique!!')]
