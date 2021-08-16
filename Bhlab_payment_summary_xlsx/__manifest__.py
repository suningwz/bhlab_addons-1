# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bhlab Excel Payment Report',
    'version': '0.1',
    'category': 'Accounting',
    'summary': 'Payment Summary Report',
    'license':'AGPL-3',
    'description': """
    Payment Summary Report
""",
    'depends': ['account'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'wizard/print_payment_summary_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
