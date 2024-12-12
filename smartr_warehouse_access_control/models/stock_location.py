from odoo import models, fields, api
from odoo.osv import expression

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_available_locations(self, user=None):
        """Get locations available to the user"""
        user = user or self.env.user
        # Use sudo to bypass company access checks
        warehouses = user.warehouse_access_ids.sudo().filtered('active').mapped('warehouse_id')
        domain = []
        if warehouses:
            domain = ['|', 
                     ('id', 'child_of', warehouses.mapped('view_location_id').ids),
                     ('id', 'parent_of', warehouses.mapped('view_location_id').ids)]
        return domain

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to handle location access"""
        domain = domain or []
        if not self.env.is_superuser():
            available_locations = self.get_available_locations()
            if available_locations:
                domain = expression.OR([domain, available_locations])
        return super(StockLocation, self.sudo()).search_read(domain=domain, fields=fields, 
                                                           offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override read_group to handle location access"""
        domain = domain or []
        if not self.env.is_superuser():
            available_locations = self.get_available_locations()
            if available_locations:
                domain = expression.OR([domain, available_locations])
        return super(StockLocation, self.sudo()).read_group(
            domain, fields, groupby, offset=offset, limit=limit, 
            orderby=orderby, lazy=lazy
        )
