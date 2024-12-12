from odoo import models, api
from odoo.osv import expression

class ReportStockQuantity(models.Model):
    _inherit = 'report.stock.quantity'

    def _select(self):
        return super()._select()

    def _with(self):
        return super()._with()

    @api.model
    def _get_location_domain(self):
        domain = super()._get_location_domain()
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouses = user.warehouse_access_ids.filtered('active').mapped('warehouse_id')
            if accessible_warehouses:
                warehouse_locations = accessible_warehouses.mapped('view_location_id')
                accessible_locations = self.env['stock.location'].search([
                    ('id', 'child_of', warehouse_locations.ids)
                ])
                domain = expression.OR([
                    domain,
                    [('location_id', 'in', accessible_locations.ids)]
                ])
        return domain
