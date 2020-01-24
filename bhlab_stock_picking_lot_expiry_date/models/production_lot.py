# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
	_inherit = 'stock.production.lot'
	_order = "expiry_date"
	
	expiry_date = fields.Datetime(string='Expiry Date',
		help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.',
		stor=True)

	available_qty = fields.Float('Quantity available', compute='_product_available_qty')

	# Assign dates according to products data
	@api.model
	def create(self, vals):
		dates = self._get_dates(vals.get('product_id'))
		for d in dates.keys():
			if not vals.get(d):
				vals[d] = dates[d]
		return super(StockProductionLot, self).create(vals)

	@api.onchange('product_id')
	def _onchange_product(self):
		_logger.warn('none> _onchange_product()')
		dates_dict = self._get_dates()
		for field, value in dates_dict.items():
			setattr(self, field, value)
	
	@api.one
	def _product_available_qty(self):
        # We only care for the quants in internal or transit locations and is_stock_quantity_not_reserved.
		quants = self.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'] and q.location_id.is_stock_quantity_not_reserved)
		self.available_qty = sum(quants.mapped('quantity'))