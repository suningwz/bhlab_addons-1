# -*- coding: utf-8 -*-
{
    'name': "bhlab Amount in Words For Invoices and Sale Orders",
    'summary': "Amount in Words For Invoices and Sale Orders",
    'description': """
	Amount in Words For Invoices and Sale Orders
    """, 
    'author': "ERPish.com",
    'website': "http://www.bhlab.bhinvest.net",
    'category': 'Sales', 
    'version': '1.0',   
    'depends': ['account', 'sale'],
    'data': [
		'views/invoice.xml',
    ],
    'installable': True,
    'application': True,   
    'auto_install': False,
}
