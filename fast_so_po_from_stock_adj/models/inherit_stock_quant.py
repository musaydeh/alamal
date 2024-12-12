from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    transit_qty = fields.Float(string="Quantity", required=False, default=1)
    available_qty = fields.Float(string="Available Quantity", compute="_compute_available_qty")
    standard_price = fields.Float(string="Unit Cost", required=False, related='product_id.standard_price',
                                  groups="alamal_hide_cost.product_cost_group")
    lst_price = fields.Float(string="Unit Price", required=False, related='product_id.lst_price')
    inventory_quantity_auto_apply = fields.Float(
        'Inventoried Quantity', digits='Product Unit of Measure',
        compute='_compute_inventory_quantity_auto_apply',
        inverse='_set_inventory_quantity', groups='base.group_user'
    )
    product_tire_brand = fields.Many2one(related="product_id.tire_brand", string="Brand", readonly=True, store=True)
    product_tire_pattern = fields.Many2one(related="product_id.tire_brand", string="Pattern", readonly=True, store=True)

    @api.depends('inventory_quantity_auto_apply', 'reserved_quantity')
    def _compute_available_qty(self):
        for rec in self:
            rec.available_qty = rec.inventory_quantity_auto_apply - rec.reserved_quantity

    def action_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartr_tires_custom_purchase_reports.action_sale_history")
        action['domain'] = [('product_id', '=', self.product_id.id), ('hide_from_sale_history', '=', False),
                            ('state', 'in', ['sale', 'done'])]
        action['display_name'] = _("Sales History for %s", self.product_id.display_name)
        return action

    def make_fast_so_wizard(self):
        view_id = self.env.ref('fast_so_po_from_stock_adj.fast_so_wizard').id
        view = {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fast.so.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_ids': self._context.get('active_ids'),
            }
        }
        return view

    def make_fast_po_wizard(self):
        view_id = self.env.ref('fast_so_po_from_stock_adj.fast_po_wizard').id
        view = {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fast.po.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_ids': self._context.get('active_ids'),
            }
        }
        return view

    def _prepare_fast_sale_order_line(self, line, sales_order):
        return {
            'create_uid': self.env.user.id,
            'write_uid': self.env.user.id,
            'product_id': line.product_id.id,
            'order_id': sales_order.id,
            'product_template_id': line.product_id.product_tmpl_id.id,
            'state': 'draft',
            'product_uom_qty': line.transit_qty,
            'route_id': self.get_route_id(line)
        }

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
            sales_order_line = self.env['sale.order.line'].sudo().create(
                self._prepare_fast_sale_order_line(line, sales_order))
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

    def get_route_id(self, stock_quant):
        route_id = self.env['stock.route'].search(
            [('sale_selectable', '=', True), ('deliver_from_warehouse', '=', stock_quant.location_id.warehouse_id.id)])
        return route_id.id if route_id else False

    def add_to_cart_fast_so(self, partner_id, lines):
        # lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        partner = self.env['res.partner'].browse(partner_id)
        sales_order = self.env.user.last_created_sale_order

        if not sales_order:
            raise ValidationError(_("You Don't Have a Cart Yet !!"))
        if sales_order.state in ['done', 'sale', 'confirmed']:
            raise ValidationError(_("Your Cart was Confirmed, Please Create new Draft Order!!"))

        for line in lines:
            sales_order_line = self.env['sale.order.line'].sudo().create(
                self._prepare_fast_sale_order_line(line, sales_order))
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

    def _prepare_fast_purchase_order_line(self, line, purchase_order):
        return {
            'product_id': line.product_id.id,
            'order_id': purchase_order.id,
            'product_qty': line.transit_qty
        }

    def make_fast_po(self, partner_id, lines):
        # lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        partner = self.env['res.partner'].browse(partner_id)
        purchase_order = self.env['purchase.order'].sudo().create({
            'partner_id': partner_id,
            'company_id': lines[0].company_id.id,
            'payment_term_id': partner.property_supplier_payment_term_id.id,
        })

        for line in lines:
            purchase_order_line = self.env['purchase.order.line'].sudo().create(
                self._prepare_fast_purchase_order_line(line, purchase_order))
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

    def action_create_fast_internal_warehouse_transfer(self):
        if len(self.location_id) > 1:
            raise ValidationError(
                _("All lines must be from the same Location to be able to create an Inter-Warehouse Transfer"))

        action = self.sudo().env.ref("fast_so_po_from_stock_adj.action_inter_warehouse_transfer_wizard")
        result = action.read()[0]

        result["context"] = {
            "default_location_id": self.location_id.id,
            "default_line_ids": [(0, 0, {"quant_id": quant.id}) for quant in self]
        }

        return result
