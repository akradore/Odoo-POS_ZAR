# -*- coding: utf-8 -*-
# © 2015 Gael Rabier
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Documents - Terms and Conditions',
    'summary': 'Add Terms and Conditions to your documents',
    'version': '10.0.1.0.0',
    'author': 'Niboo',
    'category': 'Document Management',
    'description': '''
Allows you to add Terms and Conditions to your documents.
    ''',
    'license': 'AGPL-3',
    'website': 'https://www.niboo.be/',
    'images': [
        'static/description/terms_conditions_cover.png',
    ],
    'depends': [
        'sale'
    ],
    'data': [
        'views/res_company.xml',
        'views/report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
