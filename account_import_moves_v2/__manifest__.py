# -*- coding: utf-8 -*-

{
    'name': 'Account import moves v2',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'extra',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': 'Importation des écritures comptables depuis Excel',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['account_import_model'],
    'data': [
        'views/import_moves_view.xml',
        'views/sequence.xml',
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
