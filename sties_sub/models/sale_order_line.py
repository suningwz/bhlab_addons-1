from odoo import exceptions, fields, models, api, _
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    is_standard = fields.Boolean(string='Is Standart', default=False, store=True)
    is_reactif_dedie = fields.Boolean(string='Is Standart', default=False, store=True)
    is_reactif_manuel = fields.Boolean(string='Is Standart', default=False, store=True)