# -*- coding: utf-8 -*-

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange("picking_type_id")
    def onchange_picking_type_id(self):
        self.action_suggest_route()

    def action_get_warehouses_quant(self, moves):
        warehouses_result = {}
        stock_quant_obj = self.env["stock.quant"]
        for move in moves:
            domain = [("location_id.usage", "=", "internal"), ("product_id", "=", move.product_id.id)]
            if move.lot_ids:
                domain += [("lot_id", "in", move.lot_ids.ids)]

            quants = stock_quant_obj.search(domain)
            for quant in quants:
                warehouse = quant.location_id.warehouse_id
                if warehouse not in warehouses_result:
                    warehouses_result[warehouse] = 0

                warehouses_result[warehouse] += (
                        quant.available_quantity > move.product_uom_qty and move.product_uom_qty or quant.available_quantity)

        return warehouses_result

    def action_suggest_warehouse(self):
        warehouses_result = self.action_get_warehouses_quant(self.move_ids)

        current_warehouse = False
        current_quantity = 0
        for warehouse, quantity in warehouses_result.items():
            if quantity > current_quantity or not current_warehouse:
                current_warehouse = warehouse
                current_quantity = quantity

        if current_warehouse:
            self.picking_type_id = current_warehouse.out_type_id
            self.action_suggest_route()

    def action_suggest_route(self):
        warehouse = self.picking_type_id.warehouse_id
        if not warehouse:
            return

        moves = self.move_ids
        first_route = False
        while moves:
            moves, warehouse, first_route = moves.action_suggest_route(warehouse, first_route)

    def button_validate(self):
        return super(StockPicking, self.sudo()).button_validate()
