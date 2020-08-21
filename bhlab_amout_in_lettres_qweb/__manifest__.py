{
    'name': 'Bhlab montant en lettres',
    'version': '12.0.1',
    "author" : "nadir",
    'summary': """Impression montant en lettre""",
    "website" : "http://www.bhlab.bhinvest.com",
    'description': 'Module qui permet de  convertir le montant en letrres',
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
