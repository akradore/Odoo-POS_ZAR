from odoo import models, fields, api, _
import xlsxwriter   #import xlwt #help http://nullege.com/codes/search/xlwt.Style.easyxf    http://nullege.com/codes/search/xlwt
import StringIO
import base64
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

import logging
_logger = logging.getLogger(__name__)

class tax_balance_report(models.TransientModel):
    _name = 'tax.balance.report'

    start_date = fields.Date(string = 'Start Date')
    end_date = fields.Date(string = 'End Date')
    file = fields.Binary(string="File")
    file_name = fields.Char(string="File Name", size=64, default='Tax Balance Report.xlsx')
    exported = fields.Boolean(string="Exported", default=False)
    
    @api.multi
    def print_xls_report(self):
        fl = StringIO.StringIO()
        fl.flush()
        
        wb = xlsxwriter.Workbook(fl)
        stylei = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'italic': True, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style0 = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style1 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'num_format': '#,##0.00;-#,##0.00;"-"'})
        style77 = wb.add_format({'font_name': 'Times New Roman','align': 'left', 'bold': False, 'num_format': '#,##0.00;-#,##0.00;"-"'})
#         style3 = wb.add_format({'font_name': 'Times New Roman', 'bold': False, 'num_format': '####0;-####0;"-"'})
#         style5 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'top': 1, 'bottom': 2, 'num_format': '####0;-####0;"-"'})
        style4 = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'top': 1, 'bottom': 2,                                'num_format': '#,##0.00;-#,##0.00;"-"'})
#         style_percent = wb.add_format({'num_format': '0.00%'})
#        wb = xlsxwriter.Workbook(fl)
        ws = []
#         c = -1
        row = 1
        ws.append( wb.add_worksheet('Tax Balance Report') )
        ws.append( wb.add_worksheet('Vat Exempt') )
        ws[1].set_column('A:A', 15.25)
        ws[1].set_column('B:B', 20.25)
        ws[1].set_column('C:C', 35.25)
        ws[1].set_column('D:D', 15.25)
        ws[1].set_column('E:E', 15.25)
        ws[1].set_column('F:F', 15.25)
        ws[1].set_column('G:G', 15.25)
        ws[1].set_column('H:H', 35.25)
        ws[1].set_column('I:I', 15.25)
        ws[1].write(1, 1,'Supplier/Customer' ,style0)
        ws[1].write(1, 2,'Tax Type' ,style0)
        ws[1].write(1, 3,'Transaction Type' ,style0) 
        ws[1].write(1, 4,'Transaction Ref' ,style0)
        ws[1].write(1, 5,'Invoice Posted Date' ,style0)
        ws[1].write(1, 6,'Invoice Date' ,style0)
        ws[1].write(1, 7,'Tax Account' ,style0)
        ws[1].write(1, 8,'Invoiced Amount' ,style0)
        ws[1].write(1, 9,'Supplier Invoice Ref' ,style0)
        count = 4
        ws[1].set_column('A:A', 15.25)
        ws[1].set_column('B:B', 20.25)
        ws[1].set_column('C:C', 35.25)
        ws[1].set_column('D:D', 15.25)
        invoice_id_list = []
        zero_tax_total = 0.0
        previous_tax_id = 0
        for zero_tax in self.env['account.tax'].search([('amount','=',0.0)]):
            #count += 2           
            for inv in self.env['account.invoice'].search([('amount_tax','=',0),('date_invoice','>=',self.start_date),('date', '<=', self.end_date),('state','in',('open','paid'))]):
                for line in inv.invoice_line_ids:
                    if inv.id in invoice_id_list:
                        break
                    tax_ids = []
                    for tx in line.invoice_line_tax_ids:
                        tax_ids.append(tx.id)
                    if zero_tax.id in tax_ids:
                        invoice_id_list.append(inv.id)
                        if previous_tax_id != zero_tax.id:
                            previous_tax_id = zero_tax.id
                            ws[1].write(count, 0, zero_tax.name , style0)
                            count += 1
                        if inv.partner_id:
                            ws[1].write(count, 1,inv.partner_id.name ,style0)
                        else:
                            ws[1].write(count, 1,'-' ,style0) 
                        ws[1].write(count, 2,inv.number ,style0) 
                        ws[1].write(count, 3,inv.journal_id.name,style0)
                        ws[1].write(count, 4,inv.move_id.name ,style0)
                        ws[1].write(count, 5,inv.create_date,style0) 
                        ws[1].write(count, 6,inv.date_invoice,style0) 
                        #ws[1].write(count, 7,zero_line.account_id.name,style0) 
                        
                        dr_cr_factor = 1                  
                        if inv.type in ('out_refund','in_refund'):
                            dr_cr_factor = dr_cr_factor * -1
                        
                        ws[1].write(count, 8, (inv.amount_total * dr_cr_factor) , style0)
                        if inv.type in ('in_invoice','in_refund'):
                            ws[1].write(count, 9, inv.reference , style0)
                        zero_tax_total = zero_tax_total + (inv.amount_total * dr_cr_factor)
                        count += 1
                        continue
            #zero_lines = self.env['account.move.line'].search( [('tax_line_id', '=', zero_tax.id),('date', '>=', self.start_date), 
                                                                    #('invoice_id', '!=', False),
            #                                                        ('date', '<=', self.end_date),('move_id.state','=','posted')]
            #,order = 'journal_id'
            #)

            # _logger.info('>>>>> zero_lines' + str(len(zero_lines)) + str(self.start_date) + str(self.end_date) )
            # for zero_line in zero_lines:            
            #     if zero_line.invoice_id.id not in invoice_id_list:
            #         invoice_id_list.append(zero_line.invoice_id.id)
            #     if zero_line.partner_id:
            #         ws[1].write(count, 1,zero_line.partner_id.name ,style0)
            #     else:
            #         ws[1].write(count, 1,'-' ,style0) 
            #     ws[1].write(count, 2,zero_line.name ,style0) 
            #     ws[1].write(count, 3,zero_line.journal_id.name,style0)
            #     ws[1].write(count, 4,zero_line.move_id.name ,style0)
            #     ws[1].write(count, 5,zero_line.create_date,style0) 
            #     ws[1].write(count, 6,zero_line.date,style0) 
            #     ws[1].write(count, 7,zero_line.account_id.name,style0) 
            #     invoice_amount = self.env['account.invoice'].search([('move_id', '=', zero_line.move_id.id)])
            #     if invoice_amount:
            #         dr_cr_factor = 1                    
            #         invoice_amount = invoice_amount[0]
            #         if invoice_amount.type in ('out_refund','in_refund'):
            #             dr_cr_factor = dr_cr_factor * -1
            #         invoice_amount = invoice_amount[0]
            #         ws[1].write(count, 8, (invoice_amount.amount_total * dr_cr_factor) , style0)
            #         zero_tax_total = zero_tax_total + (invoice_amount.amount_total * dr_cr_factor)
            #     count += 3
        count += 2
        ws[1].write(count, 0,"No Tax" ,style0)
        count += 1
        invoice_id_list = []
#         for zero_line in self.env['account.move.line'].search( [('tax_line_id', '=', False),('date', '>=', self.start_date),
#                                                                 ('invoice_id', '!=', False),
#                                                             ('date', '<=', self.end_date),('move_id.state','=','posted')],
#                                                                 order = 'journal_id'):
#             if zero_line.invoice_id.id not in invoice_id_list:
#                 invoice_id_list.append(zero_line.invoice_id.id)
#                 if zero_line.partner_id:
#                    ws[1].write(count, 1,zero_line.partner_id.name ,style0)
#                 else:
#                    ws[1].write(count, 1,'-' ,style0) 
#                 ws[1].write(count, 2,"" ,style0) 
#                 ws[1].write(count, 3,zero_line.journal_id.name,style0)
#                 ws[1].write(count, 4,zero_line.move_id.name ,style0)
#                 ws[1].write(count, 5,zero_line.create_date,style0) 
#                 ws[1].write(count, 6,zero_line.date,style0) 
#                 ws[1].write(count, 7,zero_line.account_id.name,style0) 
#                 invoice_amount = self.env['account.invoice'].search([('move_id', '=', zero_line.move_id.id)])
#                 if invoice_amount:
#                     invoice_amount = invoice_amount[0]
#                     ws[1].write(count, 8,invoice_amount.amount_total,style0)
#                     zero_tax_total = zero_tax_total + invoice_amount.amount_total
#                 count += 1
        ws[1].write(count, 8,zero_tax_total,style0)
#         for invoice in self.env['account.invoice'].search([('amount_tax', '=', 0.0),('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date)]):
#             ws[1].write(count, 0,invoice.date_invoice ,style0)
#             ws[1].write(count, 1,invoice.number ,style0) 
#             ws[1].write(count, 2,invoice.partner_id.name ,style0)
#             ws[1].write(count, 3,invoice.amount_total ,style0)
#             count += 1
        ws[0].set_column('A:A', 20.25)
        ws[0].set_column('B:B', 40.25)
        ws[0].set_column('C:C', 40.25)
        ws[0].set_column('D:D', 20.25)
        ws[0].set_column('E:F', 15.25)
        ws[0].set_column('G:G', 15.25)
        ws[0].set_column('H:H', 15.25)
        ws[0].set_column('I:L', 15.25)
        
#         filter_date = self.env['account.move.line'].search( [('date', '>=', self.start_date), ('date', '<=', self.end_date),('move_id.state','=','posted')])
#         print '$$$$$$$$$$$$$$$$$$$$$$$$$',filter_date
        
#         loop
        ws[0].write(0, 0, 'Company :', style1)
        ws[0].write(0, 1, self.env.user.company_id.name, style0)
        ws[0].write(1, 0, 'Printed By:', style1)
        ws[0].write(1, 1, self.env.user.name, style0) 
        ws[0].write(2, 0, 'Printed On:', style1)
        ws[0].write(2, 1, fields.Datetime.context_timestamp(self, timestamp=datetime.now()).strftime("%d %B %Y, %I:%M%p")  , style0)     
        ws[0].write(3, 0, 'Dates:', style1)
        ws[0].write(3, 1, self.start_date + " to " + self.end_date , style0)
        ws[0].write(4, 0, 'VAT Amount:', style1)
        
        ws[0].write(0, 3 , 'TAX BALANCE REPORT', style4)
        
        taxbalance =self.env['account.tax'].search([('amount','>',0.0)])
        i = 6;
        grand_total_debit = 0.0
        grand_total_credit = 0.0
        grand_total_invoice_amount = 0.0
        grand_total_exclusive_amout = 0.0

        previous_taxbalance_id = 0

        for data in taxbalance:
#             print 'nnnnnnnnnnn',data
            
            
#             taxmoveline = self.env['account.move.line'].search([('tax_line_id', '=', data.id)])
            taxmoveline = self.env['account.move.line'].search( [('tax_line_id.amount', '>=', 0.00),('tax_line_id', '=', data.id),('date', '>=', self.start_date), ('date', '<=', self.end_date),('move_id.state','=','posted')])
            total_credit = 0.0
            total_debit = 0.0
            total_invoiceamount = 0.0
            total_exclusiveamount = 0.0

            header_printed = False
            
            for taxes in taxmoveline:
                if previous_taxbalance_id != data.id and not header_printed:
                    header_printed = True
                    ws[0].write(i, 0,data.name ,style1)
                    i += 1
                    ws[0].write(i, 1,' Supplier/Customer' , style1) 
                    ws[0].write(i, 2,'Tax Type' ,style1) 
                    ws[0].write(i, 3,'Transaction Type' ,style1)
                    ws[0].write(i, 4,'Transaction Ref' ,style1)
                    ws[0].write(i, 5,'Invoice Posted Date' ,style1) 
                    ws[0].write(i, 6,'Invoice Date' ,style1)             
                    ws[0].write(i, 7,'Tax Account' ,style1) 
                    ws[0].write(i, 8,'Dr' ,style1)
                    ws[0].write(i, 9,'Cr' ,style1)
                    ws[0].write(i, 10,'Invoiced Amount' ,style1)
                    ws[0].write(i, 11,'Exclusive Amount' ,style1)
                    ws[0].write(i, 12,'Supplier Invoice Ref' ,style1)
                    i += 1
                total_credit += taxes.credit
                total_debit += taxes.debit
                grand_total_debit += taxes.debit
                grand_total_credit += taxes.credit
                
                if taxes.partner_id:
                   ws[0].write(i, 1,taxes.partner_id.name ,style0)
                else:
                   ws[0].write(i, 1,'-' ,style0) 
                   
                ws[0].write(i, 2,taxes.name ,style0)
                ws[0].write(i, 3,taxes.journal_id.name ,style0)
                ws[0].write(i, 4,taxes.move_id.name ,style0)
                ws[0].write(i, 5,taxes.create_date,style0)
                ws[0].write(i, 6,taxes.date,style0)
                
                ws[0].write(i, 7,taxes.account_id.name,style0)
                ws[0].write(i, 8,taxes.debit,style0)
                ws[0].write(i, 9,taxes.credit,style0)
                invoice_amount = self.env['account.invoice'].search([('move_id', '=', taxes.move_id.id)])
                if invoice_amount:
                    dr_cr_factor = 1                    
                    invoice_amount = invoice_amount[0]
                    if invoice_amount.type in ('out_refund','in_refund'):
                        dr_cr_factor = dr_cr_factor * -1
                    ws[0].write(i, 10, (invoice_amount.amount_total * dr_cr_factor) , style0)
                    total_invoiceamount += (invoice_amount.amount_total * dr_cr_factor)
                    grand_total_invoice_amount += (invoice_amount.amount_total * dr_cr_factor)
                    exclusive_amt = (invoice_amount.amount_untaxed * dr_cr_factor) #- (taxes.credit or taxes.debit)
                    ws[0].write(i, 11,exclusive_amt,style0)
                    if invoice_amount.type in ('in_invoice','in_refund'):
                        ws[0].write(i, 12, invoice_amount.reference , style0)
                    total_exclusiveamount += exclusive_amt
                    grand_total_exclusive_amout += exclusive_amt
                i += 1
            if total_credit or total_debit or total_invoiceamount or total_exclusiveamount:
                ws[0].write(i, 0,'Total',style1)
                ws[0].write(i, 9,total_credit,style1)
                ws[0].write(i, 8,total_debit,style1)
                ws[0].write(i, 10,total_invoiceamount,style1)
                ws[0].write(i, 11,total_exclusiveamount,style1)
                i += 2
            previous_taxbalance_id = data.id
        ws[0].write(i, 0,'Grand Total',style1)
        ws[0].write(i, 8,grand_total_debit,style1)
        ws[0].write(i, 9,grand_total_credit,style1)
        ws[0].write(i, 10,grand_total_invoice_amount,style1)
        ws[0].write(i, 11,grand_total_exclusive_amout,style1)
        ap_vat_amount = grand_total_credit - grand_total_debit
        ws[0].write(4, 1, ap_vat_amount,style77)
        
        wb.close()
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        fl.flush()
        fl.close()
        self.file = buf
        self.exported = True
        return {
                    "type": "ir.actions.do_nothing",
                }
                
	

