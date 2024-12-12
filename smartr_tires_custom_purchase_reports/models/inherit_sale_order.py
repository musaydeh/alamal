from odoo import api, fields, models


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    hide_from_sale_history = fields.Boolean(string="", )
    mrp_tag_ids = fields.Many2many("mrp.tag", string="MRP Tags")
    total_qty = fields.Float(compute="_compute_total_qty", digits="Product Unit of Measure", store=True, readonly=True)

    @api.depends("order_line.product_uom_qty")
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(line.product_uom_qty for line in order.order_line)

    @api.depends("partner_id")
    def _compute_journal_id(self):
        super()._compute_journal_id()
        for order in self:
            if order.partner_id.property_sale_journal_id:
                order.journal_id = order.partner_id.property_sale_journal_id

    @api.model
    def create(self, values):
        res = super(InheritSaleOrder, self).create(values)
        if self.env.user:
            self.env.user.last_created_sale_order = res.id
        return res

    def _prepare_purchase_order_data(self, company, company_partner):
        values = super()._prepare_purchase_order_data(company, company_partner)

        values["type_ids"] = [(6, 0, self.order_line.lot_id.source_id.ids)]
        values["mrp_tag_ids"] = [(6, 0, self.mrp_tag_ids.ids)]

        return values

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, company):
        values = super()._prepare_purchase_order_line_data(so_line, date_order, company)

        values["lot_id"] = so_line.lot_id.id

        return values
