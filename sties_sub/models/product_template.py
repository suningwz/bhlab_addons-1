from odoo import exceptions, fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    is_standard = fields.Boolean(string='Is Standart', default=False, store=True)
    is_reactif_dedie = fields.Boolean(string='Is Standart', default=False, store=True)
    is_reactif_manuel = fields.Boolean(string='Is Standart', default=False, store=True)