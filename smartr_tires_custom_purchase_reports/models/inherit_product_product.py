from odoo import fields, models, _
from odoo.exceptions import ValidationError


class InheritProductProduct(models.Model):
    _inherit = 'product.product'
    transit_qty = fields.Float(string="Quantity", required=False, default=1)

    def action_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartr_tires_custom_purchase_reports.action_sale_history")
        action['domain'] = [('product_id', '=', self.id), ('hide_from_sale_history', '=', False),
                            ('state', 'in', ['sale', 'done'])]
        action['display_name'] = _("Sales History for %s", self.name)
        return action

    def make_fast_so_wizard(self):
        view_id = self.env.ref('smartr_tires_custom_purchase_reports.fast_so_wizard_variant').id
        view = {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fast.so.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_variant_ids': self._context.get('active_ids'),
            }
        }
        return view

    def make_fast_po_wizard(self):
        view_id = self.env.ref('smartr_tires_custom_purchase_reports.fast_po_wizard_variant').id
        view = {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fast.po.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_variant_ids': self._context.get('active_ids'),
            }
        }
        return view

    def make_fast_so(self, partner_id, lines):
        # lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        partner = self.env['res.partner'].browse(partner_id)
        sales_order = self.env['sale.order'].sudo().create({
            'partner_id': partner_id,
            'company_id': lines[0].company_id.id,
            'pricelist_id': partner.property_product_pricelist.id,
            'payment_term_id': partner.property_payment_term_id.id,
        })

        for line in lines:
            sales_order_line = self.env['sale.order.line'].sudo().create({
                'product_id': line.id,
                'order_id': sales_order.id,
                'product_template_id': line.product_tmpl_id.id,
                'product_uom_qty': line.transit_qty,
                'lot_id': line.lot_id.id
            })
            line.transit_qty = 1
        view_id = self.env.ref('sale.view_order_form').id
        view = {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': view_id,
            'res_id': sales_order.id,
            'target': 'new',
        }
        return view

    def add_to_cart_fast_so(self, partner_id, lines):
        # lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        partner = self.env['res.partner'].browse(partner_id)
        sales_order = self.env.user.last_created_sale_order

        if not sales_order:
            raise ValidationError(_("You Don't Have a Cart Yet !!"))
        if sales_order.state in ['done', 'confirmed']:
            raise ValidationError(_("Your Cart was Confirmed, Please Create new Draft Order!!"))

        for line in lines:
            sales_order_line = self.env['sale.order.line'].sudo().create({
                'product_id': line.id,
                'order_id': sales_order.id,
                'product_template_id': line.product_tmpl_id.id,
                'product_uom_qty': line.transit_qty,
                'lot_id': line.lot_id.id
            })
            line.transit_qty = 1
        view_id = self.env.ref('sale.view_order_form').id
        view = {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': view_id,
            'res_id': sales_order.id,
            'target': 'new',
        }
        return view

    def view_my_cart(self):
        sales_order = self.env.user.last_created_sale_order
        view_id = self.env.ref('sale.view_order_form').id
        view = {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': view_id,
            'res_id': sales_order.id,
            'target': 'new',
        }
        return view

    def make_fast_po(self, partner_id, lines):
        partner = self.env['res.partner'].browse(partner_id)
        purchase_order = self.env['purchase.order'].sudo().create({
            'partner_id': partner_id,
            'company_id': lines[0].company_id.id,
            'payment_term_id': partner.property_supplier_payment_term_id.id,
        })

        for line in lines:
            purchase_order_line = self.env['purchase.order.line'].sudo().create({
                'product_id': line.id,
                'order_id': purchase_order.id,
                'product_qty': line.transit_qty,
                'lot_id': line.lot_id.id
            })
            line.transit_qty = 1

        view_id = self.env.ref('purchase.purchase_order_form').id
        view = {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': view_id,
            'res_id': purchase_order.id,
            'target': 'new',
        }
        return view
