from odoo import models, fields, api

class WarehouseAccess(models.Model):
    _name = 'warehouse.access'
    _description = 'Warehouse Access Rights'

    name = fields.Char(string='Access Rule Name', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True,
        domain="[('company_id', '=', source_company_id)]")
    source_company_id = fields.Many2one('res.company', string='Source Company', required=True)
    target_company_id = fields.Many2one('res.company', string='Target Company', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True,
        domain="[('company_id', '=', target_company_id)]")
    active = fields.Boolean(default=True)

    @api.constrains('user_id', 'source_company_id')
    def _check_user_company(self):
        for record in self:
            if record.user_id.company_id != record.source_company_id:
                raise ValidationError('User must belong to the source company')