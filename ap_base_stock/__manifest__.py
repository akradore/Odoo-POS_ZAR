{'name': "AP Base", 'summary': "this module serves to create standard functionality for AP-systems",
       'version': "1.0",
       'depends': ['ap_base','stock'],
       'author': "Dylan Bridge", 'contributors': "Dylan Bridge", 'maintainer': "Dylan Bridge",
       'license': 'AGPL-3',
       'website': "http://www.ap-accounting.co.za",
       'category': 'base_extension',
       'description': """
    Description text
    """,
       'data': [
#                 'ap_partner.xml',
                'ap_layout_extend.xml',
#                 'data/account_chart_template.xml',
                # 'data/account.account.template.csv',
#                 'data/account.tax.template.csv',
#                 'data/account_chart_template.yml',
                #'views/website_rebrand.xml',
                ],
       'qweb': [],
       'sequence': 10,
       'installable': True ,
       'auto_install':  False,
       'price': 10,
       'currency': 'ZAR'
       }

