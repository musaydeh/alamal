from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    warehouse_access_ids = fields.One2many('warehouse.access', 'user_id', string='Warehouse Access')
    accessible_warehouse_ids = fields.Many2many(
        'stock.warehouse', 
        string='Accessible Warehouses',
        compute='_compute_accessible_warehouses', 
        store=True,
        help="Warehouses this user can access through warehouse access rules"
    )
    
    @api.depends('warehouse_access_ids.active', 'warehouse_access_ids.warehouse_id')
    def _compute_accessible_warehouses(self):
        for user in self:
            warehouses = user.warehouse_access_ids.filtered('active').mapped('warehouse_id')
            user.accessible_warehouse_ids = [(6, 0, warehouses.ids)]

    def get_accessible_companies(self):
        """Get all companies including those from warehouse access"""
        self.ensure_one()
        company_ids = set(self.company_ids.ids)
        warehouse_companies = self.warehouse_access_ids.filtered('active').mapped('warehouse_id.company_id')
        company_ids.update(warehouse_companies.ids)
        return list(company_ids)
