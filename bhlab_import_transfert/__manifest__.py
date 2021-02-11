# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': "Import Transferts",
	'version': "12.0.0.0",
	'category': "Stock",
	'summary': "Apps helps to import transferts from excel import transfert from csv",
	'author': "BrowseInfo",
	"price": 00,
	"currency": 'DZD',
	'depends': ['base','stock'],
	'data': [
				'wizard/import_transfert_view.xml',
				'views/import_transfert_menu.xml',
				'security/groups.xml',
			],
	'demo': [],
	'qweb': [],
	'installable': True,
	'auto_install': False,
	'application': False,
	"images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
