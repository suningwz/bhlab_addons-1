# -*- coding: utf-8 -*-

{
    'name': 'Algeria - Accounting reports - G50',
    'version': '12.0',
    'category': 'Localization',
    'description': """

""",
    'author': 'Deltalog',
    'website': 'http://www.deltalog.dz/',
    'depends': ['l10n_dz_base', 'l10n_dz_reports', ],
    'data': [
        'security/ir.model.access.csv',
        'views/report_g50.xml',
        'wizard/import_params_view.xml',
        'views/param_g50_v2.xml',
        'views/menu.xml',
        'reports/report_g50.xml'
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
