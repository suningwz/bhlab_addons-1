##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    exercise = fields.Selection([(2021, '2021'),
                                (2022, '2022')], required=True)
