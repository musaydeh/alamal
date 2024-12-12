from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    # allowed_products = fields.One2many(comodel_name="product.product", inverse_name="allowed_vendor",
    #                                    string="Allowed Products", )
    customer_target = fields.Float(string="Customer Target")

    def action_dynamic_partner_ledger(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account_reports.action_account_report_partner_ledger")
        action["params"] = {
            "options": {"partner_ids": [self.id]},
            "ignore_session": "both",
        }

        return action
