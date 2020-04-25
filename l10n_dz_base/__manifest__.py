# -*- coding: utf-8 -*-


{
    'name': 'Compta DZ Base',
    'version': '11.0',
    'author': 'Deltalog Team',
    'category': 'Accounting',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Module base comptabilité Algérienne',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['account_accountant'],
    'data': [
        'views/partner_view.xml',
        'views/exercice_view.xml',
        'views/company_view.xml',
        'views/menu_view.xml',
        'security/ir.model.access.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
