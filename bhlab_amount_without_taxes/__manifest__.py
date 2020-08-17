{
    'name': 'Bhlab amout without taxes',
    'version': '12.0.1',
    "author" : "nadir",
    'summary': """Impression montant en lettre dans le Facture""",
    "website" : "http://www.bhlab.bhinvest.com",
    'description': 'Module qui permet d afficher les montants sans les taxes dans les facturees',
    'category': 'Generic Modules/Accounting',
    'depends' : [
                    'account',
                ],
    'data' : [
              'views/amount_without_taxes_view.xml',
               ],
     
    'images': ['static/description/banner.png'], 
    'application': True,
    'installable': True

}
