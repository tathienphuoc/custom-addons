from odoo import fields, models


class EstatePropertyTagModel(models.Model):
    _name="estate.property.tag.model"
    _description	= "Estate Property Tag"
    name= fields.Char(required=True)
    color= fields.Integer()
    _order = "name"
    _sql_constraints = [
        ('check_unique_name', 'unique(name)',
         'The name must be unique.')
    ]