# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present TidyWay Software Solutions. (<https://tidyway.in/>)
#
#################################################################################
import pytz
# from openerp.osv import osv
# from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import time

DEBUG = True

if DEBUG:
    import logging

    logger = logging.getLogger(__name__)


    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass

# class partner_balance_report(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context):
#         super(partner_balance_report, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'display_address':self._display_address,
#             'get_lines': self._get_lines,
#             'get_partner_aging': self._get_partner_aging
#         })
# import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class report_partner_balance_report(models.AbstractModel):

    _name = 'report.partner_balance_report.partner_balance_report'

    def _display_address(self, partner, without_company=False, context=None):
        """
        Get all partner address attributes
        """
        print 'partner.......',partner
#         partner_obj = self.pool.get('res.partner')
#         partner_rec = partner_obj.browse(self.cr, self.uid, partner)
        address = (partner.name or '',partner.street or '',partner.street2 or '',partner.city or '',partner.state_id and partner.state_id.name or '',partner.zip or '', partner.country_id and partner.country_id.name or '')
        print 'address.....',address
        return address

    def _get_lines(self, partner,statment_date):
        """
            Get all open customer invoice and customer refund invoice with balance
        """
        inv_obj = self.env['account.invoice']
        movel_obj = self.env['account.move.line']
        partner_rec = partner
        uid_rec = self.env['res.users'].browse(self._uid)
        to_currency_id = partner_rec.property_product_pricelist and partner_rec.property_product_pricelist.currency_id or uid_rec.comapny_id.currency_id

        #'unreconciled_aml_ids':fields.one2many('account.move.line', 'partner_id', domain=['&', ('reconcile_id', '=', False), '&', 
        #                    ('account_id.active','=', True), '&', ('account_id.type', '=', 'receivable'), ('state', '!=', 'draft')]),

        #regular move lines
#         moveln_ids = movel_obj.search(self.cr, self.uid, [('reconcile_id', '=', False),
#                                                           ('account_id.active','=', True),
#                                                           ('account_id.type', '=', 'receivable'),
#                                                           ('state', '!=', 'draft'),
#                                                           ('partner_id','=',partner),
#                                                           ('date','<=',statment_date)
#                                                           ],order = 'date')

        #opening balance
        moveln_ids = movel_obj.search([
                                      ('full_reconcile_id', '=', False),
#                                                           ('account_id.active','=', True),
                                      ('account_id.user_type_id.name', '=', 'Receivable'),
                                      #('invoice', '=', False),
                                      ('move_id.state', '!=', 'draft'),
                                      ('partner_id','=',partner.id),
                                      ('date','<=',statment_date),
                                      ('journal_id.type','=','situation')
                                      ],order = 'date')
        all_invoices = inv_obj.search([
#                                       ('type','in',('out_invoice','out_refund')),
                                      ('state','=','open'),
                                      ('partner_id','=',partner.id),
                                      ('residual', '!=', 0),
                                      ('date_invoice','<=',statment_date)
                                      ],order = 'date_invoice')
        all_lines = []

        balance = 0.0
        for mvl in moveln_ids:
            date_due_format = False
            if mvl.date_maturity:
                date_due_format = (datetime.strptime(mvl.date_maturity, '%Y-%m-%d')).strftime('%Y-%m-%d')
            from_currency = mvl.journal_id.currency or mvl.journal_id.company_id.currency_id
            amount_to_assing = mvl.amount_residual_currency
            if to_currency_id != from_currency:
                amount_to_assing = from_currency.compute(mvl.amount_residual_currency, to_currency_id)

            balance += amount_to_assing
            all_lines.append({
                            'date_invoice': mvl.date,
                            'number':mvl.move_id.name or mvl.move_id.ref,
                            'line_number':mvl.move_id.name or '',
                            'line_name':mvl.move_id.ref or '',
                            'line_desc': 'Number #'+(mvl.move_id.name or mvl.move_id.ref)+(date_due_format and '-Due '+date_due_format or ''),
                            # 'line_mv_name': (mvl.move_id.name or mvl.move_id.ref),
                            # 'line_mv_date': date_due_format and '-Due '+date_due_format or '',
                            'line_date': date_due_format or '',
                            'date_due':date_due_format,
                            'line_amount': amount_to_assing,
                            'amount_total': amount_to_assing,
                            #'actual_total': int(round(total_amount)),
                            'balance': balance
                               
                              })

        for inv in all_invoices:
            #total_amount = inv.amount_total
            original_invoice_amount = inv.amount_total
            total_amount = inv.residual
            if inv.currency_id.id != to_currency_id.id:
                #total_amount = inv.currency_id.compute(inv.amount_total, to_currency_id)
                total_amount = inv.currency_id.compute(inv.residual, to_currency_id)
            if inv.type == 'out_refund':
                total_amount = (-total_amount)
                original_invoice_amount = (- original_invoice_amount)
            #balance = balance + int(round(total_amount))
            balance = balance + total_amount
            date_due_format = (datetime.strptime(inv.date_due, '%Y-%m-%d')).strftime('%Y-%m-%d')
            all_lines.append({
                              'currency': to_currency_id.name,
                              'date_invoice': inv.date_invoice,
                              'number':inv.number,
                              'line_number': 'Inv #'+inv.number,
                              'line_name': 'Inv #'+inv.number,
                              'line_date': date_due_format,
                              'line_amount': str(original_invoice_amount),
                              'line_desc': 'Inv #'+inv.number+'-'+'Due '+date_due_format +'-Original Invoice'+' '+inv.currency_id.name+' '+str(original_invoice_amount),
                              'date_due':inv.date_due,
                              'amount_total': total_amount,
                              'balance': balance
                              })

        return all_lines

#         all_lines = []
#         balance = 0.0
#         for move in movel_obj.browse(self.cr, self.uid, moveln_ids):
#             #total_amount = inv.amount_total
#             total_amount = move.result
#             if move.currency_id.id and (move.currency_id.id != to_currency_id.id):
#                 #total_amount = inv.currency_id.compute(inv.amount_total, to_currency_id)
#                 total_amount = move.currency_id.compute(move.result, to_currency_id)
# #             if inv.type == 'out_refund':
# #                 total_amount = (-total_amount)
#             #balance = balance + int(round(total_amount))
#             balance = balance + total_amount
#             
#             date_due_format = False
#             if move.date_maturity:
#                 date_due_format = (datetime.strptime(move.date_maturity, '%Y-%m-%d')).strftime('%m/%d/%Y')
#             all_lines.append({
#                               'currency': to_currency_id.name,
#                               'date_invoice': move.date,
#                               'number':move.move_id.name or move.move_id.ref,
#                               'line_desc': 'Number #'+(move.move_id.name  or move.move_id.ref)+(date_due_format and '-Due '+date_due_format or ''),
#                               'date_due':date_due_format,
#                               'amount_total': total_amount,
#                               #'actual_total': int(round(total_amount)),
#                               'balance': balance
#                               })
#         return all_lines


    def _get_partner_aging(self, partner, statment_date):
        inv_obj = self.env['account.invoice']
        movel_obj = self.env['account.move.line']
        partner_rec = partner
        uid_rec = self.env['res.users'].browse( self._uid)
        to_currency_id = partner_rec.property_product_pricelist and partner_rec.property_product_pricelist.currency_id or uid_rec.comapny_id.currency_id
        moveln_ids = movel_obj.search( [
                                          ('full_reconcile_id', '=', False),
#                                           ('account_id.active','=', True),
                                          ('account_id.user_type_id.name', '=', 'Receivable'),
                                          #('invoice', '=', False),
                                          ('move_id.state', '!=', 'draft'),
                                          ('partner_id','=',partner.id),
                                          ('date','<=',statment_date),
                                          ('journal_id.type','=','situation')
                                          ],order = 'date')

        all_invoices = inv_obj.search( [
#                                       ('type','in',('out_invoice','out_refund')),
                                      ('state','=','open'),
                                      ('partner_id','=',partner.id),
                                      ('residual', '!=', 0),
                                      ('date_invoice','<=',statment_date)
                                      ],order = 'date_invoice')
        all_lines = []

        for mvl in moveln_ids:
            date_due_format = False
            if mvl.date_maturity:
                date_due_format = (datetime.strptime(mvl.date_maturity, '%Y-%m-%d')).strftime('%Y-%m-%d')

            date_due = datetime.strptime(mvl.date_maturity or mvl.date, '%Y-%m-%d')
            due_days = (datetime.strptime(statment_date, '%Y-%m-%d') - date_due).days

            from_currency = mvl.journal_id.currency or mvl.journal_id.company_id.currency_id
            amount_to_assing = mvl.amount_residual_currency
            if to_currency_id != from_currency:
                amount_to_assing = from_currency.compute(mvl.amount_residual_currency, to_currency_id)

            all_lines.append({
                            'date_invoice': mvl.date,
                            'number':mvl.move_id.name or mvl.move_id.ref,
                            'line_desc': 'Number #'+(mvl.move_id.name  or mvl.move_id.ref)+(date_due_format and '-Due '+date_due_format or ''),
                            'date_due':date_due_format,
                            'amount_total': amount_to_assing,
                            'date_due':mvl.date_maturity or mvl.date,
                            'due_days': due_days,
                            'balance': int(round(amount_to_assing)),
                            #'actual_total': int(round(total_amount)),
                               
                              })

        for inv in all_invoices:
            #calculate base on invoice date
            #calculate base on due date
            print inv,'@@@@@'
            date_due = datetime.strptime(inv['date_due'], '%Y-%m-%d')
            due_days = (datetime.strptime(statment_date, '%Y-%m-%d') - date_due).days
            #total_amount = inv.amount_total
            total_amount = inv.residual
            if inv.currency_id.id != to_currency_id.id:
                #total_amount = inv.currency_id.compute(inv.amount_total, to_currency_id)
                total_amount = inv.currency_id.compute(inv.residual, to_currency_id)
            all_lines.append({
                              'currency': to_currency_id.name,
                              'date_invoice': inv.date_invoice,
                              'date_due':inv.date_due,
                              'amount_total': total_amount,
                              #'actual_total': int(round(total_amount)),
                              'type':inv.type,
                              'balance': int(round(total_amount)),
                              'due_days': due_days
                              })

#         all_lines = []
#         for move in movel_obj.browse(self.cr, self.uid, moveln_ids):
#             #calculate base on invoice date
#             #calculate base on due date
#             due_days = -1
#             if move.date_maturity:
# 
#             #total_amount = inv.amount_total
#             total_amount = move.result
#             if move.currency_id and (move.currency_id.id != to_currency_id.id):
#                 #total_amount = inv.currency_id.compute(inv.amount_total, to_currency_id)
#                 total_amount = move.currency_id.compute(move.result, to_currency_id)
#             date_due_format = False
#             if move.date_maturity:
#                 date_due_format = (datetime.strptime(move.date_maturity, '%Y-%m-%d')).strftime('%m/%d/%Y')
#             all_lines.append({
#                               'currency': to_currency_id.name,
#                               'date_invoice': move.date,
#                               'date_due':date_due_format,
#                               'amount_total': total_amount,
#                               #'actual_total': int(round(total_amount)),
#                               'balance': int(round(total_amount)),
#                               'due_days': due_days
#                               })

            #inv['due_days'] = due_days

        a_zero,a_one2thirty,a_thirtyone2sixty,a_sixtyonetoninty,a_over90 =0.0,0.0,0.0,0.0,0.0
        for rec in all_lines:
            amount_total = rec['amount_total']
            if rec.get('type') == 'out_refund':
                amount_total = (-rec['amount_total'])
            #if rec['due_days'] <= 0:
            if rec['due_days'] <= 0:
                a_zero += amount_total
            if 0 < rec['due_days'] <= 30:
                a_one2thirty += amount_total
            if 30 < rec['due_days'] <= 60:
                a_thirtyone2sixty += amount_total
            if 60 < rec['due_days'] <= 90:
                a_sixtyonetoninty += amount_total
            if 90 < rec['due_days']:
                a_over90 += amount_total
        dbg({'0days':a_zero,
             '1to30days':a_one2thirty,
             '31to60days':a_thirtyone2sixty,
             '61to90days':a_sixtyonetoninty,
             'over90days':a_over90,
             'amountdue':a_zero + a_one2thirty + a_thirtyone2sixty+ a_sixtyonetoninty+ a_over90,
             'currency': to_currency_id.name,
             })
        return {
               '0days':a_zero,
               '1to30days':a_one2thirty,
               '31to60days':a_thirtyone2sixty,
               '61to90days':a_sixtyonetoninty,
               'over90days':a_over90,
               'amountdue':a_zero + a_one2thirty + a_thirtyone2sixty+ a_sixtyonetoninty+ a_over90,
               'currency': to_currency_id.name,
               }
        
    @api.model
    def render_html(self, docids, data=None):
#         print '@@@@@@@@@@@',data
#         print 'context',self._context
        docs = self.env['res.partner'].browse(self._context.get('active_id'))
        docargs = {
            'doc_ids': [self._context.get('active_id')],
            'doc_model': 'res.partner',
            'docs': docs,
            'display_address':self._display_address,
            'get_lines': self._get_lines,
            'get_partner_aging': self._get_partner_aging,
            'statement_date':data.get('statement_date'),
        }
        return self.env['report'].render('partner_balance_report.partner_balance_report', docargs)

# class partner_balance_report_main(osv.AbstractModel):
#     _name = 'report.partner_balance_report.partner_balance_report'
#     _inherit = 'report.abstract_report'
#     _template = 'partner_balance_report.partner_balance_report'
#     _wrapped_report_class = partner_balance_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
