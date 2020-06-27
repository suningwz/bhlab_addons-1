# -*- coding: utf-8 -*-

##############################################################################
#
#   MLMConseil, NeoPharm Extensions
#   Copyright (C) 2017, MLMConseil. All Rights Reserved
#
##############################################################################

{
    'name': "bhlab reports",

    'summary': """
        Developpement of specification for customer NEOPHARM""",

    'description': """
Main features:
======================================================

- Adds product lot tracking and expiry date to purchase order creation.
- Customizes purchase, sale, stock picking and invoice reports.
- Blocks automatic picking creation in sale and purchase order.
- Sets temporary sequence number to partial picking backorder.
    """,

    'author': "nadir",
    'website': "http://www.bhlab.bhinvest.net",

    'category': 'Warehouse',
    'version': '1.2',

    'depends': ['base', 'sale','purchase', 'account'],

    'data': [
		'security/ir.model.access.csv',
		'views/account_payment_views.xml',
		'views/purchase_views.xml',
		'views/sale_views.xml',
		'views/stock_quant_views.xml',
        'views/stock_pack_operation_views.xml',
		'views/account_invoice_views.xml',
		'views/stock_picking_views.xml',
		'reports/mlmc_neopharm_report.xml',
		'reports/report_stockpicking_operations.xml',
        'reports/report_deliveryslip.xml',
		'reports/report_invoice.xml',
		'reports/report_purchase.xml',
		'reports/sale_report_templates.xml',
        
    ],

}