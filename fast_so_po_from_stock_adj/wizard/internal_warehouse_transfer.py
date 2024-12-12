# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import ValidationError
from psycopg2 import OperationalError


class InterWarehouseTransfer(models.TransientModel):
    _name = "inter.warehouse.transfer"
    _description = "Inter-Warehouse Transfer"

    location_id = fields.Many2one("stock.location", string="Source Location", readonly=True, required=True)
    route_id = fields.Many2one("stock.route", string="Route", required=True,
                               domain="[('inter_warehouse_transfer','=',True),('rule_ids.location_dest_id','=',location_id)]")
    line_ids = fields.One2many("inter.warehouse.transfer.line", "inter_warehouse_transfer_id", string="Lines")

    def action_create_internal_warehouse_transfer(self):
        lines = self.line_ids.filtered(lambda l: l.qty > 0)
        if lines:
            procurements = []
            procurement_group_obj = self.env["procurement.group"]
            name = _("Inter-Warehouse Transfer")
            for line in lines:
                values = line._prepare_procurement_values()
                procurements.append(procurement_group_obj.Procurement(
                    line.product_id, line.qty, line.product_id.uom_id, self.location_id, name, name,
                    self.location_id.company_id, values))

            try:
                with self.env.cr.savepoint():
                    procurement_group_obj.run(procurements, raise_user_error=True)
            except ProcurementException as errors:
                message = ""
                for procurement, error_msg in errors.procurement_exceptions:
                    if message:
                        message += "\n"

                    message += error_msg

                raise ValidationError(message)
            except OperationalError:
                raise

    def action_create_internal_warehouse_transfer_and_view(self):
        self.action_create_internal_warehouse_transfer()

        lines = self.line_ids.filtered(lambda l: l.qty > 0)
        action = self.sudo().env.ref("stock.stock_picking_action_picking_type")
        result = action.read()[0]
        result["domain"] = [("move_ids.inter_warehouse_quant_id", "in", lines.quant_id.ids)]

        return result


class InterWarehouseTransferLine(models.TransientModel):
    _name = "inter.warehouse.transfer.line"
    _description = "Inter-Warehouse Transfer Line"

    inter_warehouse_transfer_id = fields.Many2one("inter.warehouse.transfer", string="Inter-Warehouse Transfer",
                                                  required=True,
                                                  ondelete="cascade")
    quant_id = fields.Many2one("stock.quant", string="Quant", required=True, readonly=True)
    product_id = fields.Many2one(related="quant_id.product_id", string="Product", store=True, readonly=True)
    lot_id = fields.Many2one(related="quant_id.lot_id", string="Lot/Serial Number", store=True, readonly=True)
    available_qty = fields.Float(related="quant_id.available_qty", string="available Quantity", store=True,
                                 readonly=True)
    qty = fields.Float(string="Quantity", required=True)

    def _prepare_procurement_values(self):
        inter_warehouse_transfer = self.inter_warehouse_transfer_id
        date = fields.Date.today()
        dates_info = self.product_id._get_dates_info(date, inter_warehouse_transfer.location_id,
                                                     route_ids=inter_warehouse_transfer.route_id)
        return {
            "route_ids": inter_warehouse_transfer.route_id,
            "date_planned": dates_info["date_planned"],
            "date_order": dates_info["date_order"],
            "date_deadline": date,
            "warehouse_id": inter_warehouse_transfer.location_id.warehouse_id,
            "inter_warehouse_quant_id": self.quant_id.id
        }
