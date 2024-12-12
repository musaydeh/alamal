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

    @api.model
    def _get_company_domain(self):
        """Override to include warehouses from accessible companies"""
        domain = super()._get_company_domain()
        if not self.env.is_superuser():
            accessible_warehouses = self.accessible_warehouse_ids
            if accessible_warehouses:
                domain = expression.OR([
                    domain,
                    [('warehouse_id', 'in', accessible_warehouses.ids)]
                ])
        return domain
