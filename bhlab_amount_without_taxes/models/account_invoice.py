from odoo import fields, api, models, _

class InvoiceOrder(models.Model):
    _inherit = 'account.invoice'
    amount_without_taxes = fields.Float(string="Montant sans taxes:", store=True, readonly=True, currency_field='currency_id', compute='_compute_amount_without_taxes')
    amount_with_taxes = fields.Float(string="Montant avec taxes:", store=True, readonly=True, currency_field='currency_id', compute='_compute_amount_without_taxes')

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_amount_without_taxes(self):
        try:
            for invoice in self:
                invoice.amount_without_taxes = 0.0
                invoice.amount_with_taxes == 0.0
                for line in invoice.invoice_line_ids:
                    if len(line.invoice_line_tax_ids) <= 1:
                        if line.invoice_line_tax_ids.amount == 0.0:
                            invoice.amount_without_taxes += line.price_subtotal
                        else:
                            invoice.amount_with_taxes += line.price_subtotal
        except Exception as e:
            pass
