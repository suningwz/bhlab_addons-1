# -*- encoding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution    
#    Copyright (C) 2004-2017 NEXTMA (http://nextma.com). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from odoo import fields, api, models, _

class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = self.currency_id.amount_to_text(self.amount_total)

    num_word = fields.Char(string="Arrêtée le présent devis à la somme de :", compute='_compute_amount_in_word')


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = self.currency_id.amount_to_text(self.amount_total)

    num_word = fields.Char(string="Arrêtée le présente Facture à la somme de :", compute='_compute_amount_in_word')


class InvoiceOrder(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = self.currency_id.amount_to_text(self.amount_total)

    num_word = fields.Char(string="Arrêtée le présente Facture à la somme de :", compute='_compute_amount_in_word')
