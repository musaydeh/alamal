from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    journal_id = fields.Many2one("account.journal", string="Billing Journal", domain=[('type', '=', 'purchase')],
                                 check_company=True, compute="_compute_journal_id", store=True, readonly=True)
    mrp_tag_ids = fields.Many2many("mrp.tag", string="MRP Tags")

    total_qty = fields.Float(compute="_compute_total_qty", digits="Product Unit of Measure", store=True, readonly=True)

    @api.depends("order_line.product_qty")
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(line.product_qty for line in order.order_line)

    @api.depends("partner_id")
    def _compute_journal_id(self):
        for order in self:
            order.journal_id = order.partner_id.property_purchase_journal_id

    @api.onchange("type_ids")
    def onchange_purchase_types(self):
        if self.type_ids:
            for line in self.order_line.filtered(lambda l: l.lot_id):
                if line.lot_id.source_id not in self.type_ids._origin:
                    line.lot_id = False

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        if self.requisition_id.type_ids:
            self.type_ids = self.requisition_id.type_ids

        super()._onchange_requisition_id()

    @api.onchange("journal_id")
    def onchange_journal_id(self):
        if self.journal_id and self.journal_id.fiscal_position_id:
            self.fiscal_position_id = self.journal_id.fiscal_position_id

    def _prepare_invoice(self):
        values = super()._prepare_invoice()

        if self.journal_id:
            values["journal_id"] = self.journal_id.id

        return values

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        values = super()._prepare_sale_order_data(name, partner, company, direct_delivery_address)

        values["mrp_tag_ids"] = [(6, 0, self.mrp_tag_ids.ids)]

        return values

    @api.model
    def _prepare_sale_order_line_data(self, line, company):
        values = super()._prepare_sale_order_line_data(line, company)

        values["lot_id"] = line.lot_id.id

        return values


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    product_tracking = fields.Selection(related='product_id.tracking', depends=['product_id'])
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number", check_company=True)

    @api.onchange("product_id")
    def onchange_product(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.lot_id = False

    @api.onchange("lot_id")
    def onchange_lot(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.product_id = self.lot_id.product_id

    def action_product_locations_report(self):
        self.ensure_one()
        domain = [('location_id.usage', '=', 'internal'), ('product_id', '=', self.product_id.id)]
        if self.lot_id:
            domain += [("lot_id", "=", self.lot_id.id)]
        view_id = self.env.ref('stock.view_stock_quant_tree').id
        view = {
            'name': 'Stock Locations',
            'type': 'ir.actions.act_window',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'view_id': view_id,
            'target': 'current',
            'domain': domain
        }
        return view
