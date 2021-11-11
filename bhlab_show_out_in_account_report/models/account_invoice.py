##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice'

    name_out = fields.Char(compute='_compute_out', store=True)

    @api.depends('invoice_id')
    def _compute_out(self):
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        print(self.origin)
        print(so)
