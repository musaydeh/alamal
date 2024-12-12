# -*- coding: utf-8 -*-

from odoo import models


class StockForecasted(models.AbstractModel):
    _inherit = 'stock.forecasted_product_product'

    def _move_domain(self, product_template_ids, product_ids, wh_location_ids):
        in_domain, out_domain = super()._move_domain(product_template_ids, product_ids, wh_location_ids)

        lot_id = self.env.context.get("lot_id", False)
        if lot_id:
            in_domain += [("move_line_ids.lot_id", "=", lot_id)]
            out_domain += [("move_line_ids.lot_id", "=", lot_id)]

        return in_domain, out_domain

    def _product_sale_domain(self, product_template_ids, product_ids):
        domain = super(StockForecasted, self)._product_sale_domain(product_template_ids, product_ids)

        lot_id = self.env.context.get("lot_id", False)
        if lot_id:
            domain += [("lot_id", "=", lot_id)]

        return domain

    def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
        res = super()._get_report_header(product_template_ids, product_ids, wh_location_ids)

        draft_purchase_order_ids = [draft_purchase_order["id"] for draft_purchase_order in
                                    res.get("draft_purchase_orders", [])]

        draft_purchase_warehouses = ""
        if draft_purchase_order_ids:
            draft_purchase_warehouses = ",".join(warehouse.display_name for warehouse in
                                                 self.env['purchase.order'].search(
                                                     [("id", "in", draft_purchase_order_ids)]).mapped(
                                                     "picking_type_id.warehouse_id"))

        res["draft_purchase_warehouses"] = draft_purchase_warehouses

        return res

    def _prepare_report_line(self, quantity, move_out=None, move_in=None, replenishment_filled=True, product=False,
                             reserved_move=False, in_transit=False, read=True):
        line = super()._prepare_report_line(quantity, move_out, move_in, replenishment_filled, product, reserved_move,
                                            in_transit, read)

        if move_out:
            picking = move_out.picking_id
            warehouse_name = picking.location_id.warehouse_id.display_name
        elif move_in:
            picking = move_in.picking_id
            warehouse_name = picking.location_dest_id.warehouse_id.display_name
        else:
            warehouse_name = self._context.get("warehouse_name", "")

        line["warehouse_name"] = warehouse_name

        return line
