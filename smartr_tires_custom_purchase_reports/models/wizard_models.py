from odoo import api, fields, models, _


class SalesOrderWizard(models.TransientModel):
    _inherit = "fast.so.wizard"

    product_variant_ids = fields.Many2many(comodel_name="product.product", string="")

    def pass_values_to_product_product_so(self):
        lines = self.product_variant_ids
        partner_id = self.partner_id.id
        return self.env['product.product'].make_fast_so(partner_id, lines)

    def pass_values_to_product_product_so_and_view(self):
        lines = self.product_variant_ids
        partner_id = self.partner_id.id
        view = self.env['product.product'].make_fast_so(partner_id, lines)
        view['target'] = 'current'
        return view

    def pass_values_to_product_product_add_to_cart(self):
        lines = self.product_variant_ids
        partner_id = self.partner_id.id
        return self.env['product.product'].add_to_cart_fast_so(partner_id, lines)
    def action_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartr_tires_custom_purchase_reports.action_sale_history")
        action['domain'] = [('product_id', '=', self.id), ('hide_from_sale_history', '=', False),
                            ('state', 'in', ['sale', 'done'])]
        action['display_name'] = _("Sales History for %s", self.display_name)
        return action
class PurchaseOrderWizard(models.TransientModel):
    _inherit = "fast.po.wizard"

    product_variant_ids = fields.Many2many(comodel_name="product.product", string="")

    def pass_values_to_product_product_po(self):
        lines = self.product_variant_ids
        partner_id = self.partner_id.id
        return self.env['product.product'].make_fast_po(partner_id, lines)

    def pass_values_to_product_product_po_and_view(self):
        lines = self.product_variant_ids
        partner_id = self.partner_id.id
        view = self.env['product.product'].make_fast_po(partner_id, lines)
        view['target'] = 'current'
        return view
