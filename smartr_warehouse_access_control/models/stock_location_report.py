from odoo import models, fields, api, tools
from odoo.osv import expression

class StockLocationReport(models.Model):
    _name = 'stock.location.report'
    _description = 'Stock Location Report'
    _auto = False
    
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)
    location_name = fields.Char(string='Location Name', readonly=True)
    company_name = fields.Char(string='Company', readonly=True)
    warehouse_name = fields.Char(string='Warehouse', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'stock_location_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stock_location_report AS (
                WITH RECURSIVE location_tree AS (
                    -- Get all locations that are directly under authorized warehouses
                    SELECT sl.id, sl.parent_path
                    FROM stock_location sl
                    JOIN stock_warehouse sw ON sl.id = sw.view_location_id
                    JOIN warehouse_access wa ON sw.id = wa.warehouse_id
                    WHERE wa.active = true
                    
                    UNION
                    
                    -- Get all child locations
                    SELECT sl.id, sl.parent_path
                    FROM stock_location sl
                    JOIN location_tree lt ON sl.parent_path LIKE lt.parent_path || '%%'
                )
                SELECT 
                    ROW_NUMBER() OVER () as id,
                    sl.id as location_id,
                    sl.name as location_name,
                    rc.name as company_name,
                    sw.name as warehouse_name,
                    sw.id as warehouse_id,
                    sq.product_id,
                    sum(sq.quantity) as quantity,
                    pt.uom_id as uom_id
                FROM stock_location sl
                JOIN location_tree lt ON sl.id = lt.id
                LEFT JOIN stock_warehouse sw ON sl.warehouse_id = sw.id
                LEFT JOIN res_company rc ON sw.company_id = rc.id
                LEFT JOIN stock_quant sq ON sq.location_id = sl.id
                LEFT JOIN product_product pp ON sq.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                GROUP BY 
                    sl.id, sl.name, rc.name, sw.name, sw.id,
                    sq.product_id, pt.uom_id
            )
        """)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Ensure user only sees authorized warehouses"""
        domain = domain or []
        if not self.env.is_superuser():
            user = self.env.user
            authorized_warehouse_ids = user.warehouse_access_ids.filtered('active').mapped('warehouse_id').ids
            domain = expression.AND([
                domain,
                [('warehouse_id', 'in', authorized_warehouse_ids)]
            ])
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Ensure user only sees authorized warehouses in grouping"""
        domain = domain or []
        if not self.env.is_superuser():
            user = self.env.user
            authorized_warehouse_ids = user.warehouse_access_ids.filtered('active').mapped('warehouse_id').ids
            domain = expression.AND([
                domain,
                [('warehouse_id', 'in', authorized_warehouse_ids)]
            ])
        return super().read_group(domain, fields, groupby, offset=offset, 
                                limit=limit, orderby=orderby, lazy=lazy)
