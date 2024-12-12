from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    """This code is added to add att name in case product name has only one value"""
    _inherit = "product.template.attribute.value"

    def _is_from_single_value_line(self, only_active=True):
        """Return False always"""
        self.ensure_one()
        return False
