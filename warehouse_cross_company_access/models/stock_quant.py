from odoo import models, api, fields
from odoo.osv import expression

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_domain_locations(self):
        domain = super()._get_domain_locations()
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

    @api.model
    def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        self = self.sudo()
        return super()._get_available_quantity(product_id, location_id, lot_id, package_id, owner_id, strict, allow_negative)

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None):
        self = self.sudo()
        return super()._update_available_quantity(product_id, location_id, quantity, lot_id, package_id, owner_id, in_date)

    @api.model
    def _get_inventory_fields_read(self):
        """ Returns a list of fields user can read on quants """
        res = super()._get_inventory_fields_read()
        res.append('location_id')
        return res
