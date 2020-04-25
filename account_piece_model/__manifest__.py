# -*- coding: utf-8 -*-


{
    'name': 'Modele piece comptable',
    'version': '11.0',
    'author': 'Deltalog Team',
    'category': 'Accounting',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Modele piece comptable',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['l10n_dz_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/piece_model_view.xml',
        'wizard/w_saisie.xml',
        'views/piece_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
