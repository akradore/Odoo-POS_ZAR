# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from ast import literal_eval

from odoo import models, fields, api
from odoo.tools import pickle as cPickle


class product_product(models.Model):
    _inherit = 'product.product'
    
    is_updated = fields.Boolean(default=False)
    is_new = fields.Boolean(default=False)
    
    @api.multi
    def write(self, vals):
        if vals.get('list_price') or vals.get('standard_price'):
            vals.update({'is_updated':True})
        res = super(product_product, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals.update({'is_new':True})
        res = super(product_product, self).create(vals)
        return res