# -*- coding: utf-8 -*-

from odoo.addons.purchase_stock.report.stock_forecasted import StockForecasted


def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
    res = super(StockForecasted, self)._get_report_header(product_template_ids, product_ids, wh_location_ids)
    domain = [('state', 'in', ['draft', 'sent', 'to approve'])]
    domain += self._product_purchase_domain(product_template_ids, product_ids)
    warehouse_id = self.env.context.get('warehouse_id', False)
    if warehouse_id:
        warehouse_id = warehouse_id if isinstance(warehouse_id, list) else [warehouse_id]
        domain += [('order_id.picking_type_id.warehouse_id', 'in', warehouse_id)]

    lot_id = self.env.context.get("lot_id", False)
    if lot_id:
        domain += [("lot_id", "=", lot_id)]

    po_lines = self.env['purchase.order.line'].search(domain)
    in_sum = sum(po_lines.mapped('product_uom_qty'))
    res['draft_purchase_qty'] = in_sum
    res['draft_purchase_orders'] = po_lines.mapped("order_id").sorted(key=lambda po: po.name).read(
        fields=['id', 'name'])
    res['draft_purchase_orders_matched'] = self.env.context.get('purchase_line_to_match_id') in po_lines.ids
    res['qty']['in'] += in_sum
    return res


setattr(StockForecasted, "_get_report_header", _get_report_header)
