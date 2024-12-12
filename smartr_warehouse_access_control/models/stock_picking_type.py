from odoo import models, api
from odoo.osv import expression

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def _search(self, domain, offset=0, limit=None, order=None):
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouse_ids = user.warehouse_access_ids.filtered('active').mapped('warehouse_id').ids
            
            domain = expression.OR([
                domain or [],
                ['|',
                 ('warehouse_id.company_id', 'in', user.company_ids.ids),
                 ('warehouse_id', 'in', accessible_warehouse_ids)]
            ])
            
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if not self.env.is_superuser():
            user = self.env.user
            accessible_warehouse_ids = user.warehouse_access_ids.filtered('active').mapped('warehouse_id').ids
            
            domain = expression.OR([
                domain or [],
                ['|',
                 ('warehouse_id.company_id', 'in', user.company_ids.ids),
                 ('warehouse_id', 'in', accessible_warehouse_ids)]
            ])
            
        return super().search_read(domain=domain, fields=fields, offset=offset, 
                                 limit=limit, order=order)
