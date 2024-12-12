from odoo import fields, models


class BrandModule(models.Model):
    _name = 'tire.brand'

    name = fields.Char(string="", required=True, )
    # pattern = fields.Char(string="", required=True, )
    patterns = fields.One2many(comodel_name="tire.pattern", inverse_name="brand", string="", store=True)


class PatternModule(models.Model):
    _name = 'tire.pattern'
    name = fields.Char(string="", required=True, )
    brand = fields.Many2one(comodel_name="tire.brand", string="", required=True, )


# TIRE WIDTH
class TireWidth(models.Model):
    _name = 'tire.width'
    name = fields.Char(string="TIRE WIDTH", required=True, )


# ASPECT RATIO
class AspectRatio(models.Model):
    _name = 'tire.aspect.ratio'
    name = fields.Char(string="ASPECT RATIO", required=True, )


# RIM DIAMETER
class RimDiameter(models.Model):
    _name = 'tire.rim.diameter'
    name = fields.Char(string="RIM DIAMETER", required=True, )


# LOAD INDEX
class LoadIndex(models.Model):
    _name = 'tire.load.index'
    name = fields.Char(string="LOAD INDEX", required=True, )


# Ply Rating
class PlyRating(models.Model):
    _name = 'tire.ply.rating'
    name = fields.Char(string="Ply Rating", required=True, )


# Speed Index
class SpeedIndex(models.Model):
    _name = 'tire.speed.index'
    name = fields.Char(string="Name", required=True, )
