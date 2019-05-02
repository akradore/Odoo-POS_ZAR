# -*- coding: utf-8 -*-


from odoo import api, models

import logging
_logger = logging.getLogger(__name__)


class payslip_report(models.AbstractModel):
    _name = 'report.pos_session_summary.report_pos_session'
    
    

    @api.model
    def render_html(self, docids, data=None):
        x = self.env['pos.session'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': 'pos.session',
            'data': data,
            'docs': x,
            
        }
        return self.env['report'].render('pos_session_summary.report_pos_session', docargs)
    
