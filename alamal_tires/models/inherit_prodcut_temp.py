from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_kind = fields.Selection([
        ("tire", "Tire"),
        ("wheel", "Wheel"),
        ("battery", "Battery")
    ], string="Product Kind", default="tire")

    r_zr = fields.Selection([
        ("r", "R"),
        ("zr", "ZR")], string="R/ZR")
    tire_width = fields.Many2one(comodel_name="tire.width", string="Tire Width", required=False, )
    aspect_ratio = fields.Many2one(comodel_name="tire.aspect.ratio", string="Aspect Ratio", required=False, )
    rim_diameter = fields.Many2one(comodel_name="tire.rim.diameter", string="Rim Diameter", required=False, )
    load_index = fields.Many2one(comodel_name="tire.load.index", string="Load Index", required=False, )
    ply_rating = fields.Many2one(comodel_name="tire.ply.rating", string="Ply Rating", required=False, )
    tire_brand = fields.Many2one(comodel_name="tire.brand", string="Brand", required=False, )
    tire_pattern = fields.Many2one(comodel_name="tire.pattern", string="Pattern", required=False)
    speed_index_id = fields.Many2one(comodel_name="tire.speed.index", string="Speed Index", required=False)
    origin = fields.Many2one(comodel_name="res.country", string="Origin", required=False, )
    allowed_patterns_ids = fields.Many2many(comodel_name="tire.pattern", string="Allowed Patterns", required=False)
    product_oe_specification_ids = fields.Many2many("product.oe.specification", string="OE Specifications")
    free_qty = fields.Float(string="Available Quantity", compute="_compute_available_qty")
    hc_capacity_40 = fields.Integer(string="40 HC Capacity")
    factory_code = fields.Char(string="Factory Code")

    @api.depends('product_variant_ids')
    def _compute_available_qty(self):
        variants_available = {
            p['id']: p for p in self.product_variant_ids._origin.read(
                ['qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty', 'free_qty'])
        }
        prod_available = {}
        for template in self:
            free_qty = 0
            for p in template.product_variant_ids._origin:
                free_qty += variants_available[p.id]["free_qty"]
            template.free_qty = free_qty

        # for rec in self:
        #     rec.available_qty = rec.inventory_quantity_auto_apply - rec.reserved_quantity

    @api.onchange('tire_brand')
    def onchange_method(self):
        self.tire_pattern = False
        if self.tire_brand:
            self.allowed_patterns_ids = self.tire_brand.patterns
        else:
            self.allowed_patterns_ids = False

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        product_templates = self.search_fetch(args + ['|', '|', '|',
                                                      # '|',
                                                      ('default_code', operator, name),
                                                      ('product_variant_ids.default_code', operator, name),
                                                      # ('product_variant_ids.second_name', operator, name),
                                                      ('name', operator, name),
                                                      ('barcode', operator, name)], ["display_name"], limit=limit)
        return [(product_template.id, product_template.display_name) for product_template in product_templates.sudo()]

    def write(self, values):
        res = super(ProductTemplate, self).write(values)

        fields_tire = ["product_kind", "tire_width", "aspect_ratio", "rim_diameter", "tire_brand", "tire_pattern",
                       "load_index", "speed_index_id", "origin", "product_oe_specification_ids", "r_zr", "ply_rating"]

        if any(field_tire in values for field_tire in fields_tire):
            for product_template in self.filtered(lambda pt: pt.product_kind == "tire"):
                product_template.write({"name": product_template._return_tire_code_name()})

        return res

    def create(self, values):
        res = super(ProductTemplate, self).create(values)

        if res.product_kind and res.product_kind == "tire":
            res.name = res._return_tire_code_name()

        return res

    @api.onchange("product_kind", "tire_width", "aspect_ratio", "rim_diameter", "tire_brand", "tire_pattern",
                  "load_index", "speed_index_id", "origin", "product_oe_specification_ids", "r_zr", "ply_rating")
    def onchange_product_tire_name(self):
        if self.product_kind == "tire":
            self.name = self._return_tire_code_name()

    def _return_tire_code_name(self):
        name_code = ""
        name_code += self.tire_width.name if self.tire_width else ""
        name_code += "/"
        name_code += self.aspect_ratio.name if self.aspect_ratio else ""
        if self.r_zr:
            name_code += self.r_zr == "zr" and "ZR" or "R"

        name_code += self.rim_diameter.name + " " if self.rim_diameter else ""
        name_code += self.tire_brand.name + " " if self.tire_brand else ""
        name_code += self.tire_pattern.name + " " if self.tire_pattern else ""
        name_code += self.load_index.name + " " if self.load_index else ""
        name_code += self.speed_index_id.name + " " if self.speed_index_id else ""
        name_code += self.ply_rating.name + " " if self.ply_rating else ""
        name_code += self.origin.name + " " if self.origin else ""

        # Add short codes for the new fields
        for product_oe_specification in self.product_oe_specification_ids:
            name_code += " %s" % product_oe_specification.name

        if name_code == "/":
            name_code = False

        return name_code
