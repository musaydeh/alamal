from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for line in self.order_line:
            if line.product_template_id and line.product_uom_qty and not line.route_id:
                raise UserError(_(
                    "Please set the Route for each order line before confirming the order !!"
                ))
        return super(SaleOrder, self).action_confirm()
