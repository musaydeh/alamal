from odoo import fields, models, tools, _


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    @tools.ormcache()
    def _get_default_category_id(self):
        return self.env["product.category"].search([("is_tire", "=", True)],
                                                   limit=1) or super()._get_default_category_id()

    categ_id = fields.Many2one(default=_get_default_category_id)
    invoice_policy = fields.Selection(default="delivery")
    tracking = fields.Selection(default="lot")
    lot_valuated = fields.Boolean(default=True)

    def action_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartr_tires_custom_purchase_reports.action_sale_history")
        action['domain'] = [('product_template_id', '=', self.id)]
        action['display_name'] = _("Sales History for %s", self.name)
        return action
