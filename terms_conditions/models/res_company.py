# -*- coding: utf-8 -*-
# © 2015 Gael Rabier, Samuel Lefever, Pierre Faniel
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    description = fields.Text('Description', translate=True)
    language_id = fields.Many2one('res.lang', 'Language')

    _sql_constraints = [(
        'unique_language',
        'unique(res_id, language_id)',
        _('You can only add one document per language'),
    )]


class ResCompany(models.Model):
    _inherit = 'res.company'

    terms_and_conditions = fields.One2many(
        'ir.attachment', compute='_compute_terms_and_conditions',
        inverse='_inverse_terms_and_conditions')

    @api.multi
    def _compute_terms_and_conditions(self):
        IrAttachment = self.env['ir.attachment']
        for company in self:
            company.terms_and_conditions = IrAttachment.search([
                ('res_model', '=', 'res.company'),
                ('type', '=', 'binary'),
                ('res_id', '=', company.id)
            ])

    @api.multi
    def _inverse_terms_and_conditions(self):
        attachments = []
        IrAttachment = self.env['ir.attachment']
        for company in self:

            terms_and_conditions = IrAttachment.search([
                ('res_model', '=', 'res.company'),
                ('type', '=', 'binary'),
                ('res_id', '=', company.id)
            ])

            for document in terms_and_conditions:
                if document not in company.terms_and_conditions:
                    document.unlink()

            for document in company.terms_and_conditions:
                if document not in terms_and_conditions:
                    language_id = document.language_id.id if \
                        document.language_id else False
                    attachments.append(IrAttachment.create({
                        'res_model': 'res.company',
                        'name': document.name,
                        'datas': document.datas,
                        'language_id': language_id,
                        'res_id': company.id,
                        'type': 'binary',
                    }))
