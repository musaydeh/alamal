from odoo import api, fields, models


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_require_app_1 = fields.Boolean(string="", )
    custom_require_app_2 = fields.Boolean(string="", )
    is_export = fields.Boolean(string="", related="fiscal_position_id.is_export")
    order_container_ids = fields.Many2many(comodel_name="sale.container", compute="_compute_order_container_ids")
    notes = fields.Char(string="Notes")

    @api.depends('order_line')
    def _compute_order_container_ids(self):
        for order in self:
            order.order_container_ids = False
            for line in order.order_line:
                if line.container_id and line.container_id not in order.order_container_ids:
                    order.order_container_ids += line.container_id

    @api.onchange('order_line')
    def onchange_method(self):
        flag1 = False
        flag2 = False
        for line in self.order_line:
            # print("Check for new line")
            # print("line.product_template_id.list_price", line.product_template_id.list_price)
            # print("line.product_template_id.standard_price", line.product_template_id.standard_price)
            # print("line.price_unit", line.price_unit)

            if line.discount:
                unit_price = line.with_company(line.company_id)._get_display_price()
                # print("unit_price", unit_price)
                list_price = unit_price if unit_price else line.product_template_id.list_price
                # print("list_price", list_price)
                price_after_disc = line.price_unit * ((100 - line.discount) / 100)

                # Check List price
                if list_price > price_after_disc:
                    flag1 = True
                    # print("self.custom_require_app_1 = True")
                # Check Cost
                if line.product_template_id.standard_price > price_after_disc:
                    flag2 = True
                    # print("self.custom_require_app_2 = True")
                # adding line field
                line.require_approval = True if list_price > price_after_disc or \
                                                line.product_template_id.standard_price > price_after_disc else False

        self.custom_require_app_1 = flag1
        self.custom_require_app_2 = flag2



    def action_view_procurement_group_button(self):
        procurement_id = self.env['procurement.group'].search([('sale_id', '=', self.id)], limit=1)
        if procurement_id:
            action_vals = {
                'type': 'ir.actions.act_window',
                'res_model': 'procurement.group',
                'view_mode': 'form',
                'res_id': procurement_id.id,
                'views': [(False, 'form')],
            }
            return action_vals
