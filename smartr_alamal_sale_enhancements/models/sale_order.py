# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_invoice_id = fields.Many2one(domain="[('parent_id','child_of',partner_id)]")
    partner_shipping_id = fields.Many2one(domain="[('parent_id','child_of',partner_id)]")

    def action_get_warehouses_quant(self, lines):
        warehouses_result = {}
        stock_quant_obj = self.env["stock.quant"]
        for line in lines:
            domain = [("location_id.usage", "=", "internal"), ("product_id", "=", line.product_id.id)]
            if line.lot_id:
                domain += [("lot_id", "=", line.lot_id.id)]

            quants = stock_quant_obj.search(domain)
            for quant in quants:
                warehouse = quant.location_id.warehouse_id
                if warehouse not in warehouses_result:
                    warehouses_result[warehouse] = 0

                warehouses_result[warehouse] += (
                        quant.available_quantity > line.product_uom_qty and line.product_uom_qty or quant.available_quantity)
        return warehouses_result

    def action_suggest_warehouse(self):
        warehouses_result = self.action_get_warehouses_quant(self.order_line.filtered(lambda l: not l.display_type))

        current_warehouse = False
        current_quantity = 0
        for warehouse, quantity in warehouses_result.items():
            if quantity > current_quantity or not current_warehouse:
                current_warehouse = warehouse
                current_quantity = quantity

        if current_warehouse:
            self.warehouse_id = current_warehouse
            self.action_suggest_route()

    def action_suggest_route(self):
        if not self.warehouse_id:
            return

        lines = self.order_line.filtered(lambda l: not l.display_type)
        warehouse = self.warehouse_id
        first_route = False
        while lines:
            lines, warehouse, first_route = lines.action_suggest_route(warehouse, first_route)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_tracking = fields.Selection(related='product_id.tracking', depends=['product_id'])
    available_lot_ids = fields.Many2many("stock.lot", compute="_compute_available_lot_ids")
    lot_id = fields.Many2one("stock.lot", string="Lot / Serial Number", check_company=True,
                             domain="[('id','in',available_lot_ids)]")

    @api.depends("product_id")
    def _compute_available_lot_ids(self):
        stock_lot_obj = self.env["stock.lot"].sudo()
        for line in self:
            domain = []
            print("slls", line.product_id)
            if line.product_id:
                domain += [("product_id", "=", line.product_id.id)]

            line.available_lot_ids = stock_lot_obj.search(domain)

    @api.depends("lot_id")
    def _compute_pricelist_item_id(self):
        lot_lines = self.filtered(
            lambda l: l.product_id and not l.display_type and l.order_id.pricelist_id and l.lot_id)
        for line in lot_lines:
            line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                line.product_id,
                quantity=line.product_uom_qty or 1.0,
                uom=line.product_uom,
                date=line.order_id.date_order,
                lot=line.lot_id
            )

        super(SaleOrderLine, self - lot_lines)._compute_pricelist_item_id()

    @api.depends("lot_id")
    def _compute_price_unit(self):
        super()._compute_price_unit()

    @api.depends("lot_id")
    def _compute_purchase_price(self):
        lines = self.filtered(lambda l: l.lot_id)
        super(SaleOrderLine, self - lines)._compute_purchase_price()

        for line in lines:
            line.purchase_price = line._convert_to_sol_currency(line.lot_id.avg_cost, line.product_id.cost_currency_id)

    @api.onchange("product_id")
    def onchange_product(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.lot_id = False

    @api.onchange("lot_id")
    def onchange_lot(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.product_id = self.lot_id.product_id

    def _get_pricelist_price(self):
        self.ensure_one()
        if self.lot_id:
            return self.order_id.pricelist_id._get_product_price(
                self.product_id.with_context(**self._get_product_price_context()),
                self.product_uom_qty or 1.0,
                currency=self.currency_id,
                uom=self.product_uom,
                date=self.order_id.date_order or fields.Date.today(),
                lot=self.lot_id
            )
        return super()._get_pricelist_price()

    def action_suggest_route(self, warehouse, first_route):
        lines = self.env["sale.order.line"]

        if warehouse:
            stock_quant_obj = self.env["stock.quant"]

            route = self.env["stock.route"].search([("sale_selectable", "=", True), ("warehouse_selectable", "=", True),
                                                    ("warehouse_ids", "in", warehouse.ids)], limit=1)
            if route:
                for line in self:
                    domain = [("location_id.warehouse_id", "=", warehouse.id), ("location_id.usage", "=", "internal"),
                              ("product_id", "=", line.product_id.id)]
                    if line.lot_id:
                        domain += [("lot_id", "=", line.lot_id.id)]

                    total_qty = sum(quant.available_quantity for quant in stock_quant_obj.search(domain))
                    if line.product_uom_qty <= total_qty:
                        line.write({"route_id": route.id})
                    else:
                        lines |= line

                if not first_route:
                    first_route = route
            elif first_route:
                self.write({"route_id": first_route.id})
        elif first_route:
            self.write({"route_id": first_route.id})

        if lines:
            warehouses_result = lines.order_id.action_get_warehouses_quant(lines)
            warehouse = False
            current_quantity = 0
            for current_warehouse, quantity in warehouses_result.items():
                if quantity > current_quantity or not current_warehouse:
                    warehouse = current_warehouse
                    current_quantity = quantity

        return lines, warehouse, first_route
