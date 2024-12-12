# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    state = fields.Selection([
        ("to_do", "To Do"),
        ("done", "Done"),
        ("cancel", "Cancelled")], compute="_compute_state", string="Status", store=True, readonly=True)
    company_id = fields.Many2one("res.company", string="Company", index=True, store=True, readonly=False,
                                 compute="_compute_company_id")
    date_order = fields.Datetime(compute="_compute_date_order", string="Order Date", readonly=True, store=True)
    expected_delivery_date = fields.Datetime(compute="_compute_expected_delivery_date", string="Expected Delivery Date",
                                             readonly=True, store=True)
    responsible_id = fields.Many2one("res.users", compute="_compute_responsible", string="Responsible", readonly=True,
                                     store=True)
    order_notes = fields.Char(compute="_compute_order_notes", string="Note from Order")

    @api.depends("sale_id.company_id", "stock_move_ids.purchase_line_id.order_id.company_id")
    def _compute_company_id(self):
        for procurement_group in self:
            company = False
            if procurement_group.sale_id:
                company = procurement_group.sale_id.company_id
            elif procurement_group.stock_move_ids.purchase_line_id:
                company = procurement_group.stock_move_ids.purchase_line_id.order_id.company_id

            procurement_group.company_id = company

    def _compute_order_notes(self):
        for procurement_group in self:
            order_notes = ""
            if procurement_group.sale_id:
                order_notes = procurement_group.sale_id.notes
            elif procurement_group.stock_move_ids.purchase_line_id:
                order_notes = procurement_group.stock_move_ids.purchase_line_id.order_id.order_notes

            procurement_group.order_notes = order_notes

    @api.depends("stock_move_ids.state")
    def _compute_state(self):
        for procurement_group in self:
            if procurement_group.stock_move_ids.filtered(lambda m: m.state not in ["done", "cancel"]):
                state = "to_do"
            elif procurement_group.stock_move_ids.filtered(lambda m: m.state == "done"):
                state = "done"
            else:
                state = "cancel"

            procurement_group.state = state

    @api.depends("sale_id.date_order", "stock_move_ids.purchase_line_id.order_id.date_order")
    def _compute_date_order(self):
        for procurement_group in self:
            date_order = False
            if procurement_group.sale_id:
                date_order = procurement_group.sale_id.date_order
            elif procurement_group.stock_move_ids.purchase_line_id:
                date_order = procurement_group.stock_move_ids.purchase_line_id.order_id.date_order

            procurement_group.date_order = date_order

    @api.depends("sale_id.commitment_date", "stock_move_ids.purchase_line_id.order_id.date_planned")
    def _compute_expected_delivery_date(self):
        for procurement_group in self:
            expected_delivery_date = False
            if procurement_group.sale_id:
                expected_delivery_date = procurement_group.sale_id.commitment_date
            elif procurement_group.stock_move_ids.purchase_line_id:
                expected_delivery_date = procurement_group.stock_move_ids.purchase_line_id.order_id.date_planned

            procurement_group.expected_delivery_date = expected_delivery_date

    @api.depends("sale_id.user_id", "stock_move_ids.purchase_line_id.order_id.user_id")
    def _compute_responsible(self):
        for procurement_group in self:
            responsible = False
            if procurement_group.sale_id:
                responsible = procurement_group.sale_id.user_id
            elif procurement_group.stock_move_ids.purchase_line_id:
                responsible = procurement_group.stock_move_ids.purchase_line_id.order_id.user_id

            procurement_group.responsible_id = responsible

    def action_print_reports(self):
        action = self.sudo().env.ref("alamal_tires.action_print_reports_from_procurement_group_wizard")
        result = action.read()[0]

        return result
