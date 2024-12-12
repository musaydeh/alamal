from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    second_name = fields.Char(compute="_compute_second_name", store=True, string="Search Name")
    free_qty_main_company = fields.Float(compute="_compute_free_qty_main_company",
                                         string="Available Quantity (Main Company)",
                                         digits='Product Unit of Measure')
    free_qty_other_companies = fields.Float(compute="_compute_free_qty_other_companies",
                                            string="Available Quantity (Other Companies)",
                                            digits='Product Unit of Measure')

    # allowed_vendor = fields.Many2one(comodel_name="res.partner", string="", required=False,
    #                                  compute="compute_allowed_vendor", store=True)

    @api.depends('tire_width', 'aspect_ratio', 'rim_diameter', 'tire_brand')
    def _compute_second_name(self):
        for rec in self:
            rec.second_name = ""
            rec.second_name += rec.tire_width.name if rec.tire_width.name else ""
            rec.second_name += rec.aspect_ratio.name if rec.aspect_ratio.name else ""
            rec.second_name += rec.rim_diameter.name if rec.rim_diameter.name else ""
            rec.second_name += rec.tire_brand.name if rec.tire_brand.name else ""

    def _compute_free_qty_main_company(self):
        for product_template in self:
            product_template.free_qty_main_company = sum(
                product_variant.free_qty_main_company for product_variant in product_template.product_variant_ids)

    def _compute_free_qty_other_companies(self):
        for product_template in self:
            product_template.free_qty_other_companies = sum(
                product_variant.free_qty_other_companies for product_variant in product_template.product_variant_ids)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        product_templates = self.search_fetch(args + ['|', ('name', operator, name), ('second_name', operator, name)],
                                              ["display_name"], limit=limit)
        return [(product_template.id, product_template.display_name) for product_template in product_templates.sudo()]

    def action_other_branches_quantity_on_hand(self):
        view_list = self.env.ref("stock.view_stock_quant_tree")
        return {
            "name": _("On Hand (Branches)"),
            "type": "ir.actions.act_window",
            "res_model": "stock.quant",
            "view_mode": "list",
            "views": [(view_list.id, "list")],
            "view_id": view_list.id,
            "domain": [("company_id", "in", self.env.user.allowed_branch_company_ids.ids),
                       ("product_tmpl_id", "=", self.id)],
            "context": {"search_default_internal_loc": 1, "search_default_on_hand": 1, "inventory_mode": True}
        }

    # @api.depends('product_template_variant_value_ids', 'product_template_attribute_value_ids',
    #              'product_template_attribute_value_ids.product_attribute_value_id.partner_id',
    #              'product_template_variant_value_ids.product_attribute_value_id.partner_id', 'combination_indices')
    # def compute_allowed_vendor(self):
    #     for rec in self:
    #         print(rec.name)
    #         print(rec.product_template_variant_value_ids)
    #         print(rec.product_template_attribute_value_ids)
    #         for variant_value in rec.product_template_attribute_value_ids:
    #             print(variant_value)
    #             print(variant_value.product_attribute_value_id)
    #             print(variant_value.product_attribute_value_id.partner_id)
    #             if variant_value.product_attribute_value_id.partner_id:
    #                 print("Setting Allowed Vendor Value")
    #                 rec.allowed_vendor = variant_value.product_attribute_value_id.partner_id.id
    #         if not rec.allowed_vendor:
    #             rec.allowed_vendor = False


class InheritProduct(models.Model):
    _inherit = 'product.product'

    free_qty_main_company = fields.Float(compute="_compute_free_qty_main_company",
                                         string="Available Quantity (Main Company)",
                                         digits='Product Unit of Measure')
    free_qty_other_companies = fields.Float(compute="_compute_free_qty_other_companies",
                                            string="Available Quantity (Other Companies)",
                                            digits='Product Unit of Measure')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        products = self.search_fetch(args + ['|', '|', '|',
                                             # '|',
                                             ('default_code', operator, name),
                                             ('second_name', operator, name),
                                             ('name', operator, name),
                                             ('barcode', operator, name)], ["display_name"], limit=limit)
        return [(product.id, product.display_name) for product in products.sudo()]

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.quantity')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_free_qty_main_company(self):
        main_company = self.env["res.company"].search([("is_main_company", "=", True)], limit=1)
        products = self.with_context(prefetch_fields=False).filtered(lambda p: p.type != 'service').with_context(
            prefetch_fields=True)
        res = products.with_user(SUPERUSER_ID).with_context(main_company_id=main_company.id)._compute_quantities_dict(
            self._context.get('lot_id'), self._context.get('owner_id'),
            self._context.get('package_id'), self._context.get('from_date'),
            self._context.get('to_date'))

        for product in products:
            product.free_qty_main_company = res[product.id]["free_qty"]

        services = self - products
        services.free_qty_main_company = 0.0

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.quantity')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_free_qty_other_companies(self):
        other_companies = self.env["res.company"].search(
            [("id", "not in", self.env.companies.ids), ("is_main_company", "=", False)])
        products = self.with_context(prefetch_fields=False).filtered(lambda p: p.type != 'service').with_context(
            prefetch_fields=True)
        res = products.with_user(SUPERUSER_ID).with_context(
            other_companies=other_companies.ids)._compute_quantities_dict(
            self._context.get('lot_id'), self._context.get('owner_id'),
            self._context.get('package_id'), self._context.get('from_date'),
            self._context.get('to_date'))

        for product in products:
            product.free_qty_other_companies = res[product.id]["free_qty"]

        services = self - products
        services.free_qty_other_companies = 0.0

    def _get_domain_locations_new(self, location_ids):
        domain_quant, domain_move_in_loc, domain_move_out_loc = super()._get_domain_locations_new(location_ids)

        lot_id = self.env.context.get("lot_id", False)
        if lot_id:
            domain_move_in_loc = expression.AND([domain_move_in_loc, [("move_line_ids.lot_id", "=", lot_id)]])
            domain_move_out_loc = expression.AND([domain_move_out_loc, [("move_line_ids.lot_id", "=", lot_id)]])

        return domain_quant, domain_move_in_loc, domain_move_out_loc
