# -*- coding: utf-8 -*-

from odoo import fields
from odoo.addons.stock.models.product import Product
from odoo.tools.float_utils import float_round


def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
    domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
    domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
    dates_in_the_past = False
    # only to_date as to_date will correspond to qty_available
    to_date = fields.Datetime.to_datetime(to_date)
    if to_date and to_date < fields.Datetime.now():
        dates_in_the_past = True

    domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
    domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
    if lot_id is not None:
        domain_quant += [('lot_id', '=', lot_id)]
    if owner_id is not None:
        domain_quant += [('owner_id', '=', owner_id)]
        domain_move_in += [('restrict_partner_id', '=', owner_id)]
        domain_move_out += [('restrict_partner_id', '=', owner_id)]
    if package_id is not None:
        domain_quant += [('package_id', '=', package_id)]
    if dates_in_the_past:
        domain_move_in_done = list(domain_move_in)
        domain_move_out_done = list(domain_move_out)
    if from_date:
        date_date_expected_domain_from = [('date', '>=', from_date)]
        domain_move_in += date_date_expected_domain_from
        domain_move_out += date_date_expected_domain_from
    if to_date:
        date_date_expected_domain_to = [('date', '<=', to_date)]
        domain_move_in += date_date_expected_domain_to
        domain_move_out += date_date_expected_domain_to

    # no standard odoo
    main_company_id = self._context.get("main_company_id", False)
    if main_company_id:
        domain_quant += [('company_id', '=', main_company_id)]
        domain_move_in += [('company_id', '=', main_company_id)]
        domain_move_out += [('company_id', '=', main_company_id)]

    other_companies = self._context.get("other_companies", [])
    if other_companies:
        domain_quant += [('company_id', 'in', other_companies)]
        domain_move_in += [('company_id', 'in', other_companies)]
        domain_move_out += [('company_id', 'in', other_companies)]

    # no standard odoo

    Move = self.env['stock.move'].with_context(active_test=False)
    Quant = self.env['stock.quant'].with_context(active_test=False)
    domain_move_in_todo = [('state', 'in',
                            ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
    domain_move_out_todo = [('state', 'in',
                             ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
    moves_in_res = {product.id: product_qty for product, product_qty in
                    Move._read_group(domain_move_in_todo, ['product_id'], ['product_qty:sum'])}
    moves_out_res = {product.id: product_qty for product, product_qty in
                     Move._read_group(domain_move_out_todo, ['product_id'], ['product_qty:sum'])}
    quants_res = {product.id: (quantity, reserved_quantity) for product, quantity, reserved_quantity in
                  Quant._read_group(domain_quant, ['product_id'], ['quantity:sum', 'reserved_quantity:sum'])}
    if dates_in_the_past:
        # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
        domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
        domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
        moves_in_res_past = {product.id: product_qty for product, product_qty in
                             Move._read_group(domain_move_in_done, ['product_id'], ['product_qty:sum'])}
        moves_out_res_past = {product.id: product_qty for product, product_qty in
                              Move._read_group(domain_move_out_done, ['product_id'], ['product_qty:sum'])}

    res = dict()
    for product in self.with_context(prefetch_fields=False):
        origin_product_id = product._origin.id
        product_id = product.id
        if not origin_product_id:
            res[product_id] = dict.fromkeys(
                ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
                0.0,
            )
            continue
        rounding = product.uom_id.rounding
        res[product_id] = {}
        if dates_in_the_past:
            qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id,
                                                                                                0.0) + moves_out_res_past.get(
                origin_product_id, 0.0)
        else:
            qty_available = quants_res.get(origin_product_id, [0.0])[0]
        reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
        res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
        res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
        res[product_id]['incoming_qty'] = float_round(moves_in_res.get(origin_product_id, 0.0),
                                                      precision_rounding=rounding)
        res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(origin_product_id, 0.0),
                                                      precision_rounding=rounding)
        res[product_id]['virtual_available'] = float_round(
            qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
            precision_rounding=rounding)

    return res


setattr(Product, "_compute_quantities_dict", _compute_quantities_dict)
