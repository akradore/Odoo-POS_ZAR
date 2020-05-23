# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present TidyWay Software Solutions. (<https://tidyway.in/>)
#
#################################################################################

from odoo.osv import osv
from odoo import api,fields
DEBUG = True

if DEBUG:
    import logging

    logger = logging.getLogger(__name__)


    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass


class partner_overdue_wizard(osv.TransientModel):
    _name = 'partner.overdue.wizard'

    statement_start_date = fields.Date('Statement start Date', required=True)
    statement_end_date = fields.Date('Statement end Date', required=True)

    
    @api.multi
    def print_report(self):
        doc_ids = self._context.get('active_ids')
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        # self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self,
                                             'partner_overdue_report.partner_overdue_report',
                                             data={'statement_start_date':self.statement_start_date,
                                                   'statement_end_date':self.statement_end_date,
                                                   'doc_ids':doc_ids})
    
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
