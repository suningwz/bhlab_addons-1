from odoo import fields, api, models, _


class InvoiceOrder(models.Model):
    _inherit = 'account.invoice'
    amount_without_taxes = fields.Float(string="Montant sans taxes:", compute='_compute_amount_without_taxes',
                                        store=True)
    amount_with_taxes = fields.Float(string="Montant sans taxes:", compute='_compute_amount_without_taxes',
                                     store=True)

    @api.depends('invoice_line_ids')
    def _compute_amount_without_taxes(self):
        self.amount_without_taxes = 0.0
        self.amount_with_taxes = 0.0
        for line in self.invoice_line_ids:
            if len(line.invoice_line_tax_ids) <= 1:
                if line.invoice_line_tax_ids.amount == 0.0:
                    self.amount_without_taxes += line.price_subtotal
                else:
                    self.amount_with_taxes += line.price_subtotal
