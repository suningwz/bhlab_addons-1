# -*- coding: utf-8 -*-

##############################################################################
#
#   MLMConseil, NeoPharm Extensions
#   Model : account
#   Copyright (C) 2017, MLMConseil. All Rights Reserved
#
##############################################################################

from odoo import models, fields, api
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):
	
	_inherit = 'account.payment'
	
	bank_id     = fields.Many2one('res.bank', string='Banque émettrice')
	payment_ref = fields.Char(string='Référence du paiement')
	hide_payment_ref = fields.Boolean(compute='_compute_hide_payment_ref',
		help="Technical field used to hide the payment ref if the selected journal is not BANK")


	@api.one
	@api.depends('journal_id')
	def _compute_hide_payment_ref(self):
		_logger.warn('account_payment->_compute_hide_payment_ref()')
		if not self.journal_id:
			ret = True
		else:
			if self.journal_id.type != 'bank':
				ret = True
			else:
				ret = False
		_logger.warn('\nnone> self.journal_id.type: %s; ret: %s',self.journal_id.type, ret)
		self.hide_payment_ref = ret
	