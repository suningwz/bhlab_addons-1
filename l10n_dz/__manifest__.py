# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

{
    'name': 'Algerie - Comptabilité',
    'version': '12',
    'category': 'Localization',
    'description': """
This is the module to manage the accounting chart for Algeria in Odoo.
========================================================================

This module applies to companies based in Algeria.
.

**Email:** contact@deltalog.dz
""",
    'author': 'Deltalog team',
    'website': 'http://www.deltalog.dz/',
    'depends': ['account', 'account_accountant', 'l10n_dz_base'],
    'data': [
        'data/l10n_dz_chart_data.xml',
        'data/account_chart_template_data.xml',
        # 'data/journaux_data.xml',
        # 'data/account_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_template_data.xml',
        'data/account_chart_template_configure_data.xml',
        'data/journaux_data.xml',
        # 'data/res.partner.csv',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
