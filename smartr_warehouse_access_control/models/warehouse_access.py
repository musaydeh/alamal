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
    company_name = fields.Char(string='Company', compute='_compute_company_name', store=True)
    active = fields.Boolean(default=True, index=True, tracking=True)
    notes = fields.Text(tracking=True)
    
    @api.depends('warehouse_id')
    def _compute_company_name(self):
        for record in self:
            record.company_name = record.sudo().warehouse_id.company_id.name

    @api.depends('user_id.name', 'warehouse_id.name', 'company_name')
    def _compute_display_name(self):
        for access in self:
            if access.user_id and access.warehouse_id:
                access.display_name = f"{access.user_id.name} - {access.warehouse_id.name} ({access.company_name})"
            else:
                access.display_name = False

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
