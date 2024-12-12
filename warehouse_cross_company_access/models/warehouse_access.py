from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class WarehouseAccess(models.Model):
    _name = 'warehouse.access'
    _description = 'Warehouse Access'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade', 
                              index=True, tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, 
                                   ondelete='cascade', index=True, tracking=True)
    company_id = fields.Many2one('res.company', related='warehouse_id.company_id', 
                                 store=True, index=True)
    active = fields.Boolean(default=True, index=True, tracking=True)
    notes = fields.Text(tracking=True)

    def _get_warehouse_domain(self):
        """Get domain for warehouse selection"""
        user_companies = self.user_id.company_ids.ids if self.user_id else []
        return [('company_id', 'not in', user_companies)]
    
    @api.depends('user_id.name', 'warehouse_id.name')
    def _compute_display_name(self):
        for access in self:
            if access.user_id and access.warehouse_id:
                access.display_name = f"{access.user_id.name} - {access.warehouse_id.name}"
            else:
                access.display_name = False

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Filter warehouses not in user's companies"""
        if not self.user_id:
            return {'domain': {'warehouse_id': []}}
            
        return {
            'domain': {
                'warehouse_id': self._get_warehouse_domain()
            }
        }

    @api.constrains('user_id', 'warehouse_id')
    def _check_warehouse_company(self):
        for access in self:
            if access.warehouse_id.company_id in access.user_id.company_ids:
                raise ValidationError(_(
                    "Cannot grant access to warehouse %(warehouse)s for user %(user)s because "
                    "it belongs to one of the user's companies. Access rules are only for cross-company access.",
                    warehouse=access.warehouse_id.display_name,
                    user=access.user_id.display_name
                ))
            
    _sql_constraints = [
        ('unique_user_warehouse', 'unique(user_id, warehouse_id)', 
         'A user can only have one access rule per warehouse!')
    ]
