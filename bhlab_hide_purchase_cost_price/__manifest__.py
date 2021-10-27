# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    'name': "Hide purchase and Cost Price of the Product",
    'author': 'Ascetic Business Solution',
    'category': 'Sales',
    'summary': """Hide purchase and Cost Price of the Product""",
    'license': 'AGPL-3',
    'website': 'http://www.bhlab-algeria.com',
    'description': """
""",
    'version': '1.0',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/show_purchase_cost_price_fields.xml',
        'views/product_price_view.xml',
        'views/account_invoice_supplier_view.xml',
        'views/purchase_order_price_view.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
