from odoo import fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    hide_from_sale_history = fields.Boolean(string="", related="order_id.hide_from_sale_history", store=True)

    def action_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartr_tires_custom_purchase_reports.action_sale_history")
        action['domain'] = [('product_id', '=', self.product_id.id), ('hide_from_sale_history', '=', False),
                            ('state', 'in', ['sale', 'done'])]
        action['display_name'] = _("Sales History for %s", self.product_id.display_name)
        return action

    def action_product_locations_report(self):
        self.ensure_one()
        domain = [('location_id.usage', '=', 'internal'), ('product_id', '=', self.product_id.id)]
        if self.lot_id:
            domain += [("lot_id", "=", self.lot_id.id)]

        view_id = self.env.ref('stock.view_stock_quant_tree').id
        view = {
            'name': 'Stock Locations',
            'type': 'ir.actions.act_window',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'view_id': view_id,
            'target': 'current',
            'domain': domain
        }
        return view
