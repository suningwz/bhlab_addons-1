from odoo import exceptions, fields, models, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    _customer_selection_list = [('pub','PUB'),('priv','PRIV')]
    customer_type = fields.Selection(_customer_selection_list, string='Type', default='priv', store=True)