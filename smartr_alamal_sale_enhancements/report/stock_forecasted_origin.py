# -*- coding: utf-8 -*-

from odoo.addons.stock.report.stock_forecasted import StockForecasted


def _get_report_data(self, product_template_ids=False, product_ids=False):
    assert product_template_ids or product_ids
    res = {}

    if self.env.context.get('warehouse_id', []):
        warehouses = self.env['stock.warehouse'].search([('id', 'in', self.env.context['warehouse_id'])])
    else:
        warehouses = self.env['stock.warehouse'].search([['active', '=', True]])

    wh_location_ids = []
    for warehouse in warehouses:
        wh_location_ids += [loc['id'] for loc in
                            self.env['stock.location'].search_read([('id', 'child_of', warehouse.view_location_id.id)],
                                                                   ['id'])]
    # any quantities in this location will be considered free stock, others are free stock in transit
    res.update(self._get_report_header(product_template_ids, product_ids, wh_location_ids))
    lines = []

    for warehouse in warehouses:
        wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
            [('id', 'child_of', warehouse.view_location_id.id)],
            ['id'],
        )]
        wh_stock_location = warehouse.lot_stock_id

        lines += self.with_context(warehouse_name=warehouse.display_name)._get_report_lines(product_template_ids,
                                                                                            product_ids,
                                                                                            wh_location_ids,
                                                                                            wh_stock_location)

    res['lines'] = lines
    return res


setattr(StockForecasted, "_get_report_data", _get_report_data)
