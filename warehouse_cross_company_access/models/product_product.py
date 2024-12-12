from odoo import models, api
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(self, lot_id=None, owner_id=None, package_id=None, from_date=False, to_date=False):
        domain_quant = []
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouses = user.warehouse_access_ids.filtered('active').mapped('warehouse_id')
            if accessible_warehouses:
                warehouse_locations = accessible_warehouses.mapped('view_location_id')
                accessible_locations = self.env['stock.location'].search([
                    ('id', 'child_of', warehouse_locations.ids)
                ])
                domain_quant = expression.OR([
                    domain_quant,
                    [('location_id', 'in', accessible_locations.ids)]
                ])
        
        return super(ProductProduct, self.with_context(domain_quant=domain_quant))._compute_quantities_dict(
            lot_id=lot_id, owner_id=owner_id, package_id=package_id, from_date=from_date, to_date=to_date)

    def _compute_quantities(self):
        domain_quant = self.env.context.get('domain_quant', [])
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouses = user.warehouse_access_ids.filtered('active').mapped('warehouse_id')
            if accessible_warehouses:
                warehouse_locations = accessible_warehouses.mapped('view_location_id')
                accessible_locations = self.env['stock.location'].search([
                    ('id', 'child_of', warehouse_locations.ids)
                ])
                domain_quant = expression.OR([
                    domain_quant,
                    [('location_id', 'in', accessible_locations.ids)]
                ])
        
        return super(ProductProduct, self.with_context(domain_quant=domain_quant))._compute_quantities()
