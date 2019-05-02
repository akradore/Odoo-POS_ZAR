# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quant Management',
    'version': '1.0',
    'summary': 'Inventory, Logistics, Warehousing',
    'description': """

    """,
#     'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['account','stock'],
    'category': 'Warehouse',
    'sequence': 13,
    'data': [
#         'views/invoice.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
