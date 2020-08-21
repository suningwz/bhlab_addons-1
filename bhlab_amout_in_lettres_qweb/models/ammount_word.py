from odoo import fields, api, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_letter = fields.Char(string="Arrêtée le présent devis à la somme de :", compute='get_amount_letter')

    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        #self.amount_letter = self.currency_id.amount_to_text(self.amount_total)
        return self.amount_letter


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_letter = fields.Char(string="Arrêtée le présent devis à la somme de :", compute='get_amount_letter')

    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        self.amount_letter = self.currency_id.amount_to_text(self.amount_total)
        return self.amount_letter


class InvoiceOrder(models.Model):
    _inherit = 'account.invoice'

    amount_letter = fields.Char(string="Arrêtée le présent devis à la somme de :", compute='get_amount_letter')

    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        self.amount_letter = self.currency_id.amount_to_text(self.amount_total)
        return self.amount_letter
