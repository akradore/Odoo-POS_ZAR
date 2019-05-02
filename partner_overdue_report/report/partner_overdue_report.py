# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present TidyWay Software Solutions. (<https://tidyway.in/>)
#
#################################################################################
DEBUG = True

if DEBUG:
    import logging

    logger = logging.getLogger(__name__)


    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass

from odoo import fields, api, models, _
from datetime import datetime, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class report_partner_overdue_report(models.AbstractModel):

    _name = 'report.partner_overdue_report.partner_overdue_report'

    # def _get_account_move_lines(self, partner,partner_ids):
    def _get_account_move_lines(self, start_date, end_date, partner_ids):
        start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT).date()
#         partner_ids = kwargs.get('partner_ids')
#         start_date = kwargs.get('start_date')
#         end_date = kwargs.get('end_date')
        res = dict(map(lambda x:(x,[]), partner_ids))
        self.env.cr.execute("SELECT m.name AS move_id, l.date, l.name, l.ref, l.date_maturity, l.partner_id, l.blocked, l.amount_currency, l.currency_id, "
            "CASE WHEN at.type = 'receivable' "
                "THEN SUM(l.debit) "
                "ELSE SUM(l.credit * -1) "
            "END AS debit, "
            "CASE WHEN at.type = 'receivable' "
                "THEN SUM(l.credit) "
                "ELSE SUM(l.debit * -1) "
            "END AS credit, "
            "CASE WHEN l.date_maturity > %s and l.date_maturity < %s "
                "THEN SUM(l.debit - l.credit) "
                "ELSE 0 "
            "END AS mat "
            "FROM account_move_line l "
            "JOIN account_account_type at ON (l.user_type_id = at.id) "
            "JOIN account_move m ON (l.move_id = m.id) "
            "WHERE l.date_maturity > %s and l.date_maturity < %s AND l.partner_id IN %s AND at.type IN ('receivable', 'payable') AND NOT l.reconciled GROUP BY l.date, l.name, l.ref, l.date_maturity, l.partner_id, at.type, l.blocked, l.amount_currency, l.currency_id, l.move_id, m.name", 
            (((start_date, )+ (end_date, ) + (start_date, )+ (end_date, ) + (tuple(partner_ids),))))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        dbg(res)
        return res



    @api.model
    def render_html(self, docids, data=None):
        start_date = data.get('statement_start_date')
        end_date = data.get('statement_end_date')
        partner_ids = data.get('doc_ids')
        new_partner_ids = []
        for old_partner in partner_ids:
            if (self._get_account_move_lines(start_date=start_date,end_date=end_date,partner_ids=[old_partner])).get(old_partner):
                new_partner_ids.append(old_partner)
        partner_ids = new_partner_ids
        docs = self.env['res.partner'].browse(partner_ids)
        # dbg(self.env['res.partner'].search(['id','=',data.get('active_ids')]))
        totals = {}
        lines = self._get_account_move_lines(start_date=start_date,end_date=end_date,partner_ids=partner_ids)
        lines_to_display = {}
        company_currency = self.env.user.company_id.currency_id
        for partner_id in partner_ids:
            lines_to_display[partner_id] = {}
            totals[partner_id] = {}
            for line_tmp in lines[partner_id]:
                line = line_tmp.copy()
                currency = line['currency_id'] and self.env['res.currency'].browse(line['currency_id']) or company_currency
                if currency not in lines_to_display[partner_id]:
                    lines_to_display[partner_id][currency] = []
                    totals[partner_id][currency] = dict((fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
                if line['debit'] and line['currency_id']:
                    line['debit'] = line['amount_currency']
                if line['credit'] and line['currency_id']:
                    line['credit'] = line['amount_currency']
                if line['mat'] and line['currency_id']:
                    line['mat'] = line['amount_currency']
                lines_to_display[partner_id][currency].append(line)
                if not line['blocked']:
                    totals[partner_id][currency]['due'] += line['debit']
                    totals[partner_id][currency]['paid'] += line['credit']
                    totals[partner_id][currency]['mat'] += line['mat']
                    totals[partner_id][currency]['total'] += line['debit'] - line['credit']
        data.update({'docs':docs})
        docargs = {
            # 'doc_ids': [self._context.get('active_id')],
            'doc_ids': partner_ids,
            'doc_model': 'res.partner',
            'data':data,
            'docs': docs,
            'time': time,
            'Lines': lines_to_display,
            'Totals': totals,
            'Date': fields.date.today(),
        }
        return self.env['report'].render('partner_overdue_report.partner_overdue_report', docargs)

#     @api.model
#     def render_html(self, docids, data=None):
#         dbg('render_html')
# #         print '@@@@@@@@@@@',data
# #         print 'context',self._context
#         docs = self.env['res.partner'].browse(self._context.get('active_id'))
#         docargs = {
#             'doc_ids': [self._context.get('active_id')],
#             'doc_model': 'res.partner',
#             'docs': docs,
#             'display_address':self._display_address,
#             'get_lines': self._get_lines,
#             'get_partner_aging': self._get_partner_aging,
#             'statement_date':data.get('statement_date'),
#         }
#         return self.env['report'].render('partner_overdue_report.partner_overdue_report', docargs)

    def _display_address(self, partner, without_company=False, context=None):
        dbg('_display_address')
        # dbg(partner)
        """
        Get all partner address attributes
        """
#         partner_obj = self.pool.get('res.partner')
#         partner_rec = partner_obj.browse(self.cr, self.uid, partner)
        address = (partner.name or '',partner.street or '',partner.street2 or '',partner.city or '',partner.state_id and partner.state_id.name or '',partner.zip or '', partner.country_id and partner.country_id.name or '')
        return address

    def _get_lines(self, partner,statment_date):
        dbg('_get_lines')
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
                                      ('type','in',('out_invoice','out_refund')),
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