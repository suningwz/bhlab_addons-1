# -*- coding: utf-8 -*-
# Part of Sties. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Gestion des appels d\'offres clients',
    'version':'1.0',
    'category': 'CRM',
    'author': "Sties",
    
    'description': """
Gestion des appels d\'offres clients
==================
    """,
    
    'depends': ['sale','crm', 'sale_crm'],
    'data': [
        'data/crm_lead_data.xml',
        'security/sties_tenders_security.xml',
        'security/ir.model.access.csv',   
        'wizard/tender_lost_views.xml',
        'wizard/tender_partial_won_views.xml',
        'wizard/generate_contract_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
        'views/lost_reason_views.xml',
        'views/tender_contract_view.xml',
        'views/sties_tenders_view.xml',
        'views/link_sales_order_view.xml',
        'views/private_mad_contract_view.xml'
    ],
    'auto_install': True,
    'installable': True,
}

