from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError

class SalesOrderWizard(models.TransientModel):
    _name = "fast.so.wizard"
    partner_id = fields.Many2one(comodel_name="res.partner", string="")
    product_ids = fields.Many2many(comodel_name="stock.quant", string="")

    def pass_values_to_stock_quant_so(self):
        lines = self.product_ids
        if not self.partner_id:
            raise ValidationError(_("You have to enter a partner to create SO!!"))
        partner_id = self.partner_id.id
        return self.env['stock.quant'].make_fast_so(partner_id, lines)

    def pass_values_to_stock_quant_so_and_view(self):
        lines = self.product_ids
        if not self.partner_id:
            raise ValidationError(_("You have to enter a partner to create SO!!"))
        partner_id = self.partner_id.id
        view = self.env['stock.quant'].make_fast_so(partner_id, lines)
        view['target'] = 'current'
        return view
    def pass_values_to_add_to_cart(self):
        lines = self.product_ids
        partner_id = 1
        return self.env['stock.quant'].add_to_cart_fast_so(partner_id, lines)


class PurchaseOrderWizard(models.TransientModel):
    _name = "fast.po.wizard"
    partner_id = fields.Many2one(comodel_name="res.partner", string="")
    product_ids = fields.Many2many(comodel_name="stock.quant", string="", )

    def pass_values_to_stock_quant_po(self):
        lines = self.product_ids
        if not self.partner_id:
            raise ValidationError(_("You have to enter a partner to create PO!!"))
        partner_id = self.partner_id.id
        return self.env['stock.quant'].make_fast_po(partner_id, lines)

    def pass_values_to_stock_quant_po_and_view(self):
        lines = self.product_ids
        if not self.partner_id:
            raise ValidationError(_("You have to enter a partner to create PO!!"))
        partner_id = self.partner_id.id
        view = self.env['stock.quant'].make_fast_po(partner_id, lines)
        view['target'] = 'current'
        return view
