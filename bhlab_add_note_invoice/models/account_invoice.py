##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    note = fields.Text('Notes')
