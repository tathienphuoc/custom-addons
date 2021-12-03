from odoo import fields, models,api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError

class EstatePropertyOfferModel(models.Model):
    _name="estate.property.offer.model"
    _description	= "Estate Property Offer"
    price= fields.Float(required=True)
    status	=fields.Selection([('accepted','Accepted'),('refused','Refused')],copy=False)
    partner_id=fields.Many2one('res.partner',required=True)
    property_id=fields.Many2one('estate.property.model',required=True,ondelete="cascade")
    validity=fields.Integer(default=7)
    date_deadline= fields.Date(compute='_date_deadline', inverse="_validity")
    property_type_id=fields.Many2one('estate.property.type.model', related='property_id.property_type_id',store=True)

    _order = "price desc"
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)',
         'The offer price must be strictly positive.')
    ]
    
    @api.depends('create_date','validity')
    def _date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline=record.create_date.date()+relativedelta(days=record.validity)
            else:
                record.date_deadline=datetime.today()+relativedelta(days=record.validity)
    def _validity(self):
        for record in self:
            if record.create_date:
                record.validity=(record.date_deadline-record.create_date.date()).days
            else:
                record.validity=(record.date_deadline-datetime.today()).days
    
        
    def accept(self):
        for record in self:
            for offer in record.property_id.offer_ids.filtered_domain([('id', '!=', record.id)]):
                # offer.status='refused'
                offer.write({'status':'refused'})
            record.status='accepted'
            record.property_id.selling_price=record.price
            record.property_id.status='offer accepted'
            property_id = record.property_id.id
        return True
    
    def refuse(self):
        for record in self:
            if record.status=='accepted':
                record.property_id.selling_price=0
            record.status='refused'
        return True
                
    @api.model
    def create(self, vals):
        best_price=self.env['estate.property.model'].browse(vals['property_id']).best_price
        # print(self.env['estate.property.model'].browse(vals['property_id']))
        # print(best_price)
        if vals['price'] <= best_price:
            raise UserError(_('The offer must be higher than {}.'.format(best_price) ))
        self.env['estate.property.model'].browse(vals['property_id']).status = 'offer received'
        return super(EstatePropertyOfferModel, self).create(vals)
