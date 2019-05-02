# -*- coding: utf-8 -*-
# © 2015 Gael Rabier, Pierre Faniel, Jérôme Guerriat
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import logging
import os
import tempfile
from contextlib import closing

from cStringIO import StringIO
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval as eval
from pyPdf import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class IrActionsReportXML(models.Model):
    _inherit = 'ir.actions.report.xml'

    add_terms_conditions = fields.Boolean(string='add Terms and Conditions',
                                          default=False)
    terms_conditions_language_field = fields.Char('Language field')


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        report = self._get_report_from_name(report_name)

        if report.add_terms_conditions:
            if len(docids) > 1:
                # Super get_pdf() merges multiple record prints to one, so we
                # need to call it one by one, add the terms&conditions for each
                # and merge all together afterwards, using the same procedure
                # with temp files etc as in the super get_pdf()
                temporary_files = []
                for docid in docids:
                    report_pdf = super(Report, self).get_pdf(
                        [docid], report_name, html, data)
                    pdf_incl_terms = self.add_terms_and_conditions(
                        docid, report_pdf, report)

                    pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                        suffix='.pdf', prefix='report.tmp.')
                    with closing(
                            os.fdopen(pdfreport_fd, 'w')) as report_file:
                        report_file.write(pdf_incl_terms)

                    temporary_files.append(pdfreport_path)

                entire_report_path = self._merge_pdf(temporary_files)
                with open(entire_report_path, 'rb') as pdfdocument:
                    content = pdfdocument.read()
                # Manual cleanup of the temporary files
                for temporary_file in temporary_files:
                    try:
                        os.unlink(temporary_file)
                    except (OSError, IOError):
                        _logger.error(
                            'Error when trying to remove file %s'
                            % temporary_file)
                return content
            else:
                report_pdf = super(Report, self).get_pdf(
                    docids, report_name, html, data)
                return self.add_terms_and_conditions(docids, report_pdf,
                                                     report)
        else:
            return super(Report, self).get_pdf(docids, report_name, html, data)

    @api.model
    def add_terms_and_conditions(self, docid, original_report_pdf,
                                 original_report):
        model = original_report.model
        object = self.env[model].browse(docid)
        company = object.company_id
        if not company.terms_and_conditions:
            return original_report_pdf

        language_field = original_report.terms_conditions_language_field

        localdict = {'o': object}
        eval('document_language = o.%s' % language_field, localdict,
             mode='exec', nocopy=True)
        document_language = localdict.get('document_language',
                                          self._context.get('lang'))

        # Try to find the terms and condition matching the document_language
        terms_and_conditions = company.terms_and_conditions.filtered(
            lambda t: t.language_id.code == document_language)
        if not terms_and_conditions:
            # Try to find the default terms and conditions (no language set)
            terms_and_conditions = company.terms_and_conditions.filtered(
                lambda t: not t.language_id)
            if not terms_and_conditions:
                return original_report_pdf

        terms_and_conditions_decoded = base64.decodestring(
            terms_and_conditions.datas)

        if terms_and_conditions_decoded:
            writer = PdfFileWriter()
            stream_original_report = StringIO(original_report_pdf)
            reader_original_report = PdfFileReader(stream_original_report)
            stream_terms_and_conditions = StringIO(
                terms_and_conditions_decoded)
            reader_terms_and_conditions = PdfFileReader(
                stream_terms_and_conditions)
            for page in range(0, reader_original_report.getNumPages()):
                writer.addPage(reader_original_report.getPage(page))

            for page in range(0, reader_terms_and_conditions.getNumPages()):
                writer.addPage(reader_terms_and_conditions.getPage(page))

            stream_to_write = StringIO()
            writer.write(stream_to_write)

            combined_pdf = stream_to_write.getvalue()

            return combined_pdf
        else:
            return original_report_pdf
