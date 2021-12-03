from typing import Sequence
from odoo import fields, models,api


class EstatePropertyTypeModel(models.Model):
    _name="estate.property.type.model"
    _description	= "Estate Property Type"
    _order = "name"
    name= fields.Char(required=True)
    sequence= fields.Integer()
    property_ids=fields.One2many("estate.property.model", "property_type_id")
    offer_ids=fields.One2many("estate.property.offer.model", "property_type_id")
    offer_count=fields.Integer(compute="_offer_count")
    @api.depends('offer_ids')
    def _offer_count(self):
        self.offer_count=len(self.offer_ids)
    def open_offers(self):
        template_id = self.offer_ids.mapped('id')
        return {
            'name':'Property Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer.model',
            'view_mode': 'tree',
            'res_id': template_id,
        }