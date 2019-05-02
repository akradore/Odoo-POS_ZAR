# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from datetime import date


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def check_limit(self):
        """Check if credit limit for partner was exceeded."""
        self.ensure_one()
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.\
            search([('partner_id', '=', partner.id),
                    ('account_id.user_type_id.type', 'in',
                    ['receivable', 'payable']),
                    ('full_reconcile_id', '=', False)])
        
        debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now().date(), DF)
        for line in movelines:
            if line.date_maturity < today_dt:
                credit += line.debit
                debit += line.credit
                
                
#        
        if (credit - debit + self.amount_total) > partner.credit_limit:
            # Consider partners who are under a company.
            if partner.over_credit or (partner.parent_id
                                       and partner.parent_id.over_credit):
                
                 
                
                partner.write({
                    'credit_limit': credit - debit + self.amount_total})
                return True
            
            else:
                msg = '''%s Cannot confirm Sale Order,Total mature due Amount
                 %s as on %s !\nCheck Partner Accounts or Credit
                 Limits !''' % (partner.over_credit,
                                credit - debit, today_dt)
                raise UserError(_('Credit Over Limits !\n' + msg))
           
        else:
            return True
    
    @api.multi
    def check_invoice_limit(self):
        
        customer = self.partner_id
        credit_limit = self.partner_id.credit_limit
        order_amount = self.amount_total
        open_credit = 0
        past_due_invoices = self.env['account.invoice'].search([
                    ('type', '=', 'out_invoice'),
                    ('company_id', '=', self.company_id.id),
                    ('partner_id', '=', customer.id),
                    ('state', 'in', ['open']),
#                     '|', 
#                     ('payment_term_id', '=', False),
#                     ('date_due', '<', date.today()),
                ])
        for invoice in past_due_invoices:
                   amount = invoice.residual
                   open_credit += amount
        exceeded_credit = (open_credit + order_amount) - credit_limit
        if exceeded_credit > 0:
            msg = " Cannot confirm Invoice, Customer has Exceeded Credit Limit "
            raise UserError(_('Credit Over Limits !\n' + msg))
                
        
       

    @api.multi
    def action_invoice_open(self):
        for order in self:
            order.check_invoice_limit()
        return super(account_invoice, self).action_invoice_open()


#     @api.multi
#     def action_confirm(self):
#         """Extend to check credit limit before confirming sale order."""
#         for order in self:
#             order.check_limit()
#         return super(SaleOrder, self).action_confirm()