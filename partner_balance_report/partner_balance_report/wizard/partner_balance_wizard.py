# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present TidyWay Software Solutions. (<https://tidyway.in/>)
#
#################################################################################

from openerp.osv import osv
from openerp import api,fields

class partner_balance_wizard(osv.TransientModel):
    _name = 'partner.balance.wizard'

    statement_date = fields.Date('Statement Date', required=True)
    
    
    @api.multi
    def print_report(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'partner_balance_report.partner_balance_report',data={'statement_date':self.statement_date})
    
#     @api.multi
#     def print_report(self):
#         """
#             Print report either by warehouse or product-category
#         """
#         assert len(self) == 1, 'This option should only be used for a single id at a time.'
#         datas = {
#                  'form': 
#                         {
#                             'id': self.id,
#                             'partner_ids': self._context.get('active_ids'),
#                             'statement_date': self.statement_date,
#                         }
#                 }

#         return self.pool['report'].get_action(self._cr, self._uid, [], 'partner_balance_report.partner_balance_report', data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
