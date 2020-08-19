from odoo import fields, api, models, _


class InvoiceOrder(models.Model):
    _inherit = 'account.invoice'
    amount_without_taxes = fields.Float(string="Montant sans taxes:", compute='_compute_amount_without_taxes')
    amount_with_taxes = fields.Float(string="Montant avec taxes:", compute='_compute_amount_without_taxes')

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_amount_without_taxes(self):

        amount_without_taxes = 0.0
        amount_with_taxes = 0.0
        try:
            for invoice in self:
                for line in invoice.invoice_line_ids:
                    if len(line.invoice_line_tax_ids) <= 1:
                        if line.invoice_line_tax_ids.amount == 0.0:
                            amount_without_taxes += line.price_subtotal
                        else:
                            amount_with_taxes += line.price_subtotal

                invoice.update({
                    'amount_without_taxes': amount_without_taxes,
                    'amount_with_taxes': amount_with_taxes
                })
        except Exception as e:
            pass
