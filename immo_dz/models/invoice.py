# -*- coding: utf-8 -*-

from odoo import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def asset_create(self):
        # a la validation de la facture d'achat, créer autant d'investissements que produits achetés (quantité)
        if self.asset_category_id:
            nbr = int(self.quantity)
            for i in range(0, nbr):
                vals = {
                    'name': self.name,
                    'code': self.invoice_id.number or False,
                    'category_id': self.asset_category_id.id,
                    'value': self.price_subtotal_signed / nbr,
                    'partner_id': self.invoice_id.partner_id.id,
                    'company_id': self.invoice_id.company_id.id,
                    'currency_id': self.invoice_id.company_currency_id.id,
                    'date': self.invoice_id.date_invoice,
                    'invoice_id': self.invoice_id.id,
                }
                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
                if self.asset_category_id.open_asset:
                    asset.validate()
        return True
