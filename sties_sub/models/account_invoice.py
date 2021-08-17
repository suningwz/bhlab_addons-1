# -*- coding: utf-8 -*-
# Part of Sties. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"   

    contract_id = fields.Many2one('tender.contract', string='Contrat')
