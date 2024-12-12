from odoo import fields, models, api


class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    require_approval = fields.Boolean(string="", )
    container_id = fields.Many2one(comodel_name="sale.container", string="Container", required=False, )
    no_containers = fields.Float(string="No. of Containers", compute="_compute_no_containers", store=True,
                                 readonly=False)

    @api.depends("product_id", "product_uom_qty")
    def _compute_no_containers(self):
        for line in self:
            hc_capacity_40 = line.product_id.hc_capacity_40
            line.no_containers = hc_capacity_40 != 0 and (line.product_uom_qty / hc_capacity_40) or 0
