# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        domain = super()._get_applicable_rules_domain(products, date, **kwargs)
        lot = kwargs.get("lot", False)

        if lot:
            domain += ["|", ('lot_id', "=", False), ("lot_id", "=", lot.id)]

        return domain


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(selection_add=[("4_lot", "Lot / Serial Number")],
                                  ondelete={"4_lot": "set default"})
    available_lot_ids = fields.Many2many("stock.lot", compute="_compute_available_lot_ids")
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number",
                             ondelete="cascade", check_company=True, domain="[('id','in',available_lot_ids)]",
                             help="Specify a lot if this rule only applies to one lot. Keep empty otherwise.")

    @api.depends("product_tmpl_id", "product_id", "applied_on")
    def _compute_available_lot_ids(self):
        stock_lot_obj = self.env["stock.lot"]
        for item in self:
            domain = []
            if item.product_tmpl_id:
                domain += [("product_id.product_tmpl_id", "=", item.product_tmpl_id.id)]
            elif item.product_id:
                domain += [("product_id", "=", item.product_id.id)]

            item.available_lot_ids = stock_lot_obj.search(domain)

    @api.constrains("lot_id")
    def _check_product_consistency(self):
        super()._check_product_consistency()

        for item in self:
            if item.applied_on == "4_lot" and not item.lot_id:
                raise ValidationError(_("Please specify lot/serial number for which this rule should be applied"))

    @api.depends("lot_id")
    def _compute_name(self):
        super()._compute_name()

        for item in self:
            if item.lot_id and item.applied_on == "4_lot":
                item.name = _("Lot / Serial Number: %s", item.lot_id.display_name)

    @api.onchange("product_tmpl_id", "product_id", "applied_on")
    def onchange_method(self):
        if self.lot_id and self.lot_id not in self.available_lot_ids._origin:
            self.lot_id = False

    @api.onchange("display_applied_on")
    def _onchange_display_applied_on(self):
        super()._onchange_display_applied_on()

        for item in self:
            if item.display_applied_on == "2_product_category":
                item.update(dict(
                    lot_id=None
                ))

    @api.onchange("lot_id")
    def _onchange_rule_content(self):
        super()._onchange_rule_content()

        if not self.env.context.get('default_applied_on', False):
            lots_rules = self.filtered("lot_id")
            if lots_rules:
                lots_rules.update({"applied_on": "4_lot"})

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('applied_on', False):
                applied_on = values['applied_on']
                if applied_on != "4_lot":
                    values.update(dict(lot_id=None))
                else:
                    values.update(dict(categ_id=None))

        return super().create(vals_list)

    def write(self, values):
        if values.get('applied_on', False):
            applied_on = values['applied_on']
            if applied_on != "4_lot":
                values.update(dict(lot_id=None))
            else:
                values.update(dict(categ_id=None))

        return super().write(values)
