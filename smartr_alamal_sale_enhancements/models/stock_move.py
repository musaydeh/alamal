# -*- coding: utf-8 -*-

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_suggest_route(self, warehouse, first_route):
        moves = self.env["stock.move"]

        if warehouse:
            stock_quant_obj = self.env["stock.quant"]

            route = self.env["stock.route"].search([("sale_selectable", "=", True), ("warehouse_selectable", "=", True),
                                                    ("warehouse_ids", "in", warehouse.ids)], limit=1)
            if route:
                for move in self:
                    domain = [("location_id.warehouse_id", "=", warehouse.id), ("location_id.usage", "=", "internal"),
                              ("product_id", "=", move.product_id.id)]
                    if move.lot_ids:
                        domain += [("lot_id", "in", move.lot_ids.ids)]

                    total_qty = sum(quant.available_quantity for quant in stock_quant_obj.search(domain))
                    if move.product_uom_qty <= total_qty:
                        move.write({"route_id": route.id})
                    else:
                        moves |= move

                if not first_route:
                    first_route = route
            elif first_route:
                self.write({"route_id": first_route.id})
        elif first_route:
            self.write({"route_id": first_route.id})

        if moves:
            warehouses_result = moves.picking_id.action_get_warehouses_quant(moves)
            warehouse = False
            current_quantity = 0
            for current_warehouse, quantity in warehouses_result.items():
                if quantity > current_quantity or not current_warehouse:
                    warehouse = current_warehouse
                    current_quantity = quantity

        return moves, warehouse, first_route
