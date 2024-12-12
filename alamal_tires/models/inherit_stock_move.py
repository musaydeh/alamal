from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    route_id = fields.Many2one(comodel_name="stock.route", related="sale_line_id.route_id", string="Route",
                               readonly=False, )
    sale_id = fields.Many2one(related="sale_line_id.order_id", string="Sales Order", store=True)

    def action_product_locations_report(self):
        self.ensure_one()
        domain = [('location_id.usage', '=', 'internal'), ('product_id', '=', self.product_id.id)]
        if self.lot_ids:
            domain += [("lot_id", "in", self.lot_ids.ids)]

        return {
            'name': 'Stock Locations',
            'type': 'ir.actions.act_window',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'view_id': self.env.ref('stock.view_stock_quant_tree').id,
            'target': 'current',
            'domain': domain
        }

    def button_validate(self):
        return self.picking_id.button_validate()
