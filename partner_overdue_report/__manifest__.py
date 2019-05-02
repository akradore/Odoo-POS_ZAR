# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present TidyWay Software Solutions. (<https://tidyway.in/>)
#
#################################################################################

{
    'name': 'Partner Balance overdue Report',
    'version': '2.0',
    'category': 'account',
    'summary': 'Partner Outstanding Report',
    'description': """
Partner balance with aging analysis report.
==============================================
""",
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'depends': ['account'],
    'data': [
        'wizard/partner_overdue_wizard.xml',
        'partner_report.xml',
        'views/partner_overdue_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
