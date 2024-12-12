from odoo import models, api
from odoo.osv import expression

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Override search to include companies from accessible warehouses"""
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouse_companies = user.warehouse_access_ids.filtered('active').mapped('warehouse_id.company_id')
            
            domain = expression.OR([
                domain or [],
                ['|',
                 ('id', 'in', user.company_ids.ids),
                 ('id', 'in', accessible_warehouse_companies.ids)]
            ])
            
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to include companies from accessible warehouses"""
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouse_companies = user.warehouse_access_ids.filtered('active').mapped('warehouse_id.company_id')
            
            domain = expression.OR([
                domain or [],
                ['|',
                 ('id', 'in', user.company_ids.ids),
                 ('id', 'in', accessible_warehouse_companies.ids)]
            ])
            
        return super().search_read(domain=domain, fields=fields, offset=offset, 
                                 limit=limit, order=order)
