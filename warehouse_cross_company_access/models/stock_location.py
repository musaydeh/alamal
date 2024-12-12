from odoo import models, fields, api
from odoo.osv import expression

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def _read_group_process_groupby(self, gb, query):
        """Override to handle company access in group by"""
        if gb == 'company_id':
            return self.env['res.company'].sudo()._search([], order='name')
        return super()._read_group_process_groupby(gb, query)

    def _search(self, domain, offset=0, limit=None, order=None):
        """Override search to include locations from accessible warehouses"""
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouses = user.warehouse_access_ids.filtered('active').mapped('warehouse_id')
            
            if accessible_warehouses:
                warehouse_locations = accessible_warehouses.mapped('view_location_id')
                domain = expression.OR([
                    domain or [],
                    ['|', '|', '|',
                     ('company_id', '=', False),
                     ('company_id', 'in', user.company_ids.ids),
                     ('id', 'child_of', warehouse_locations.ids),
                     ('id', 'parent_of', warehouse_locations.ids)]
                ])
            
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override to handle company access in grouping"""
        result = super(StockLocation, self.sudo()).read_group(
            domain, fields, groupby, offset=offset, limit=limit, 
            orderby=orderby, lazy=lazy
        )
        return result

    def name_get(self):
        """Override to ensure access to location names"""
        return super(StockLocation, self.sudo()).name_get()
