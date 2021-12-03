from odoo import fields, models,api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError

class User(models.Model):
    _inherit="res.users"
    property_ids=fields.One2many("estate.property.model", "salesperson_id")