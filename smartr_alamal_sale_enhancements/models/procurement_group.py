# -*- coding: utf-8 -*-

from odoo import models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def action_print_so_all_deliveries(self):
        if not self.sale_id:
            return

        return self.env.ref("smartr_alamal_sale_enhancements.action_report_so_all_deliveries").report_action(
            self.sale_id.id)
