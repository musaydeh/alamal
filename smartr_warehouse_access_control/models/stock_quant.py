from odoo import models, api
from odoo.osv import expression

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to handle quant access"""
        domain = domain or []
        if not self.env.is_superuser():
            location_obj = self.env['stock.location']
            available_locations = location_obj.get_available_locations()
            if available_locations:
                domain = expression.AND([
                    domain,
                    [('location_id', 'child_of', self.env['stock.location'].search(available_locations).ids)]
                ])
        return super(StockQuant, self.sudo()).search_read(domain=domain, fields=fields, 
                                                         offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override read_group to handle quant access"""
        domain = domain or []
        if not self.env.is_superuser():
            location_obj = self.env['stock.location']
            available_locations = location_obj.get_available_locations()
            if available_locations:
                domain = expression.AND([
                    domain,
                    [('location_id', 'child_of', self.env['stock.location'].search(available_locations).ids)]
                ])
        return super(StockQuant, self.sudo()).read_group(
            domain, fields, groupby, offset=offset, limit=limit, 
            orderby=orderby, lazy=lazy
        )
