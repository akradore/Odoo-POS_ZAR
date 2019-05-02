 
from odoo import models, fields, api
import datetime


class res_partner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char('Vat')
    reg = fields.Char('Registration')

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    
    @api.one
    def load_default_za_values(self):
#         currency = self.env['res.currency'].search([('name', '=', 'ZAR')])
        currency_id = self.env.ref('base.ZAR')
        if currency_id:
            currency_id.rate = 1.000000
            currency_id.position = 'before'
            self.currency_id = currency_id
        lang_us = self.env.ref('base.lang_en')
        for data in self.env['res.lang'].search([]):
            data.date_format = '%Y/%m/%d'
