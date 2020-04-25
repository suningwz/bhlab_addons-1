# -*- coding: utf-8 -*-

{
    'name': 'Account import model',
    'version': '13.0',
    'author': 'Deltalog Team',
    'category': 'Account',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Modele d\'importation des ecritures comptables depuis Excel',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['l10n_dz_base'],
    'data': [
        'data/data.xml',
        'views/import_model_view.xml',
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
