# -*- coding: utf-8 -*-


{
    'name': 'Cloture exercice comptable',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'Account',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Procédure de cloture d un exercice comptable',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['l10n_dz_base', ],
    'data': [
        'views/cloture_view.xml',
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
