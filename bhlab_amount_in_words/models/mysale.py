# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import api, models,fields
from odoo.exceptions import UserError 
from odoo import exceptions
import math
import logging
_logger = logging.getLogger(__name__) 

class MyInvoice(models.Model):
	_inherit = "account.invoice"
	
	@api.one
	@api.depends('amount_total')
	def _compute_amount_words(self):
		lang = self.env.user.lang
		lang = 'fr'
		try:
			tmp= num2words(math.floor(self.amount_total), lang=lang, to='currency')
			tmp=tmp.replace('euros','dinars algériens')
			tmp=tmp.replace('euro','dinar algérien')
			cents=self.amount_total-math.floor(self.amount_total)
			_logger.debug('\n\n\n\n cents 1 :'+str(cents))
			if cents>0:
				_logger.debug('\n\n\n\n cents 2 :'+str(math.floor(cents*100)))
				tmp=tmp+' et '+num2words(round(cents*100), lang=lang)+' centimes'
			self.num_word=tmp
		except NotImplementedError:
			self.num_word = num2words(self.amount_total, lang="en", to='currency')
				
	num_word=fields.Char(string='Total en lettre:',compute='_compute_amount_words')
	

class MySale(models.Model):
	_inherit = "sale.order"	
	
	@api.one
	@api.depends('amount_total')
	def _compute_amount_words(self):
		lang = self.env.user.lang
		lang = 'fr'
		try:
			tmp= num2words(math.floor(self.amount_total), lang=lang, to='currency')
			tmp=tmp.replace('euros','dinars algériens')
			tmp=tmp.replace('euro','dinar algérien')
			cents=self.amount_total-math.floor(self.amount_total)
			_logger.debug('\n\n\n\n cents 1 :'+str(cents))
			if cents>0:
				_logger.debug('\n\n\n\n cents 2 :'+str(math.floor(cents*100)))
				tmp=tmp+' et '+num2words(round(cents*100), lang=lang)+' centimes'
			self.num_word=tmp
		except NotImplementedError:
			self.num_word = num2words(self.amount_total, lang="en", to='currency')
				
	num_word=fields.Char(string='Total en lettre:',compute='_compute_amount_words')
			
class MyPayment(models.Model):
	_inherit = "account.payment"
	num_word=fields.Char(string='Total en lettre:',compute='_compute_amount_words')
	
	@api.one
	@api.depends('amount')
	def _compute_amount_words(self):
		lang = self.env.user.lang
		lang = 'fr'
		try:
			tmp= num2words(math.floor(self.amount_total), lang=lang, to='currency')
			tmp=tmp.replace('euros','dinars algériens')
			tmp=tmp.replace('euro','dinar algérien')
			cents=self.amount_total-math.floor(self.amount_total)
			_logger.debug('\n\n\n\n cents 1 :'+str(cents))
			if cents>0:
				_logger.debug('\n\n\n\n cents 2 :'+str(math.floor(cents*100)))
				tmp=tmp+' et '+num2words(round(cents*100), lang=lang)+' centimes'
			self.num_word=tmp
		except NotImplementedError:
			self.num_word = num2words(self.amount, lang="en", to='currency')
