# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date
from odoo import api, fields, models
import base64


class CustomerOutstandingStatementWizard(models.TransientModel):
    """Customer Outstanding Statement wizard."""

    _name = 'customer.outstanding.statement.wizard'
    _description = 'Customer Outstanding Statement Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )

    date_end = fields.Date(required=True,
                           default=fields.Date.to_string(date.today()))
    show_aging_buckets = fields.Boolean(string='Include Aging Buckets',
                                        default=True)
    number_partner_ids = fields.Integer(
        default=lambda self: len(self._context['active_ids'])
    )
    filter_partners_non_due = fields.Boolean(
        string='Don\'t show partners with no due entries', default=True)

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()

    def _prepare_outstanding_statement(self):
        self.ensure_one()
        return {
            'date_end': self.date_end,
            'company_id': self.company_id.id,
            'partner_ids': self._context['active_ids'],
            'show_aging_buckets': self.show_aging_buckets,
            'filter_non_due_partners': self.filter_partners_non_due,
        }

    def _export(self):
        """Export to PDF."""
        data = self._prepare_outstanding_statement()
        return self.env['report'].with_context(landscape=True).get_action(
            self, 'customer_outstanding_statement.statement', data=data)

    def button_send_mail(self):
        
        mail_temp_obj = self.env['mail.template']
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']
        if self._context['active_ids']:
            for partner in self.env['res.partner'].browse(self._context['active_ids']):
                data = self._prepare_outstanding_statement()
                data['partner_ids'] = [partner.id]
                attachments = []
                template = self.env.ref('customer_outstanding_statement.action_print_customer_outstanding_statement', False)
                report_name = mail_temp_obj.render_template(template.report_name, template.model, partner.id)
                report = template
                report_service = report.report_name
                Template = self.env['mail.template']
                if report.report_type in ['qweb-html', 'qweb-pdf']:
                    result, format = self.env['report'].get_pdf([partner.id], report_service,data=data), 'pdf'
                else:
                    result, format = odoo_report.render_report(self._cr, self._uid, [partner.id], report_service, {'model': template.model}, Template._context)
 
                # TODO in trunk, change return format to binary to match message_post expected format
                result = base64.b64encode(result)
                if not report_name:
                    report_name = 'report.' + report_service
                ext = "." + format
                if not report_name.endswith(ext):
                    report_name += ext
                attachments.append((report_name, result))
#                 results[res_id]['attachments'] = attachments
                recipient_ids = [(4, partner.id) ]
#                 values.update(email_values or {})
                attachment_ids = []
                attachments = attachments
                mail = Mail.create({})
                print mail
                for attachment in attachments:
                    attachment_data = {
                        'name': attachment[0],
                        'datas_fname': attachment[0],
                        'datas': attachment[1],
                        'type': 'binary',
                        'res_model': 'mail.message',
                        'res_id': mail.mail_message_id.id,
                    }
                    kk = Attachment.create(attachment_data).id
                    print kk
                    attachment_ids.append(kk)
                    print attachment_ids
                if attachment_ids:
#                     values['attachment_ids'] = [(6, 0, attachment_ids)]
                    mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
                mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
                body_html = "<p>Dear %(title)s,<br><br><p><br></p></p><p>Please follow below attachments,<br></p>" % {
                    'title': partner.name,
                }
                mail.write({'body_html': body_html,'recipient_ids':recipient_ids})
                mail.send()
                attachments = False
                template = False
                report_name = False
                report = False
                result = False
                attachment_ids = False
