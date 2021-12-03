from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models,api,_
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_compare,float_is_zero
class EstatePropertyModel(models.Model):
    _name="estate.property.model"
    _description	= "Estate Property"
    _rec_name	= "title"
    property_type_id=fields.Many2one('estate.property.type.model')
    tag_ids=fields.Many2many('estate.property.tag.model')
    buyer_id=fields.Many2one('res.partner',copy=False)
    salesperson_id=fields.Many2one('res.users',default=lambda self: self.env.user)
    offer_ids=fields.One2many("estate.property.offer.model", "property_id")
    title=fields.Char(required=True)
    description=fields.Text()
    postcode	= fields.Char()
    date_availability	= fields.Date(copy=False,default=datetime.today()+relativedelta(months=3))
    expected_price	=fields.Float(required=True)
    selling_price	=fields.Float(readonly=True,copy=False)
    bedrooms	=fields.Integer(default=2)
    living_area	=fields.Integer()
    facades	=fields.Integer()
    garage	=fields.Boolean()
    garden	=fields.Boolean()
    garden_area	=fields.Integer()
    garden_orientation	=fields.Selection([('north','North'), ('south','South'), ('east','East'), ('west','West')])
    status	=fields.Selection([('new','New'),('offer received','Offer Received'), ('offer accepted','Offer Accepted'), ('sold','Sold'), ('canceled','Canceled')],copy=False,required=True,default='new')
    active	=fields.Boolean('Active',default=True)
    total_area=fields.Float()
    best_price=fields.Float(compute='_best_price',default=0)
    _order = "id desc"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'The property expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price > 0)',
         'The property selling price must be positive.'),
        ('check_unique_title', 'unique(title)',
         'The title must be unique.')
    ]
    
    @api.onchange('living_area','garden_area')
    def _compute_total(self):
        for record in self:
            record.total_area=record.living_area+record.garden_area
    
    @api.depends('offer_ids')
    def _best_price(self):
        self.best_price=0
        for record in self:
            for offer in record.offer_ids:
                if offer.price > record.best_price:
                    record.best_price=offer.price
        
    @api.onchange("garden")
    def _onchange_garden(self):
        if(self.garden):
            self.garden_area = 10
            self.garden_orientation = 'north'   
        else:
            self.garden_area = 0
            self.garden_orientation = ''   
            
    def cancel(self):
        for record in self:
            if record.status=='sold':
                raise UserError(_('Sold properties cannot be sold canceled.'))
            else:
                record.status = "canceled"
        return True
    
    def sold(self):
        for record in self:
            if record.status=='canceled':
                raise UserError(_('Canceled properties cannot be sold.'))
            elif float_compare(record.selling_price, 0,precision_digits=3)==0:
                raise UserError(_('The offer is not available.'))
            else:
                record.status = "sold"
        return True
    
        
    @api.constrains('selling_price') 
    def _check_selling_price(self):   
        for record in self:
            if float_compare(record.selling_price, (record.expected_price/100)*90,precision_digits=3)<=0:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price")

    def unlink(self):
        if self.status not in ['new','canceled']:
            raise UserError(_("Only new and canceled properties can be deleted"))
        return super(EstatePropertyModel, self).unlink()