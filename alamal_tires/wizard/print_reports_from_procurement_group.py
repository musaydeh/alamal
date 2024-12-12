# -*- coding: utf-8 -*-
from odoo import models, fields


class PrintReportsFromProcurementGroupWizard(models.TransientModel):
    _name = "print.reports.from.procurement.group"
    _description = "Print Reports from Procurement Group"

    report_id = fields.Many2one("ir.actions.report", string="Report", required=True,
                                domain=[("print_from_procurement_group", "=", True),
                                        ("model", "in", ["sale.order", "stock.picking"])])

    def print_report(self):
        group = self.env["procurement.group"].browse(self._context.get("active_ids"))

        if self.report_id.model == "sale.order":
            return self.env.ref(self.report_id.get_external_id().get(self.report_id.id)).report_action(group.sale_id)
        elif self.report_id.model == "stock.picking":
            return self.env.ref(self.report_id.get_external_id().get(self.report_id.id)).report_action(
                group.stock_move_ids.picking_id)

        return True
