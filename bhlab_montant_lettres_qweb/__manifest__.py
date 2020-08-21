{
    'name': 'Bhlab montant en lettres',
    'version': '12.0.1',
    "author" : "nadir",
    'summary': """Impression montant en lettre dans le Facture""",
    "website" : "http://www.bhlab.bhinvest.com",
    'description': 'Module qui permet de  convertir le montant d/une facture en lettres et l"ajoute  a la facture',
    'category': 'Generic Modules/Accounting',
    'depends' : [
                    'sale_management',
                    'purchase',
                    'account',
                ],
    'data' : [
            'views/amount_word_view.xml',
            'views/report_invoice.xml',
               ],
     
    'images': ['static/description/banner.png'], 
    'application': True,
    'installable': True
}
