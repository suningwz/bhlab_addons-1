# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
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
	reserved_qty = fields.Float('Reserved available', compute='_product_available_qty')

	#_alert_date = fields.Date(string='Alert Date', help='Technical field for xml view decorator', compute='_compute_alert_date')
	_alert_date = fields.Datetime(string='Alert Date')


	@api.onchange('expiry_date','_alert_date')
	def _check_alert_date(self):
		if not (self.expiry_date and self._alert_date):
				return
		if self.expiry_date < self._alert_date:
			self._alert_date = ''
			return {'warning': {
				'title':   "Incorrect date value",
				'message': "Expiry date is earlier then alert date",
			}}

	@api.onchange('expiry_date')
	def _compute_alert_date(self):
		_logger.warn('none> _compute_alert_date()')
		param = self.env['ir.config_parameter'].sudo()
		product_expiry_alert_time = int(param.get_param('product_expiry_alert_time.product_expiry_alert_time'))

		_logger.warn('\ninfo> product_expiry_alert_time: %s;',product_expiry_alert_time)
		for spl in self:
			if spl.expiry_date:
				spl._alert_date = fields.Date.to_string(fields.Date.from_string(spl.expiry_date) - datetime.timedelta(days = product_expiry_alert_time))
				#_logger.warn('\ninfo> expiry_date: %s; _alert_date: %s',spl.expiry_date, spl._alert_date)
				spl.removal_date = spl.expiry_date
	
	def _get_dates(self, product_id=None):
		"""Returns dates based on number of days configured in current lot's product."""
		mapped_fields = {
			'expiry_date': 'expiry_time'
		}
		res = dict.fromkeys(mapped_fields.keys(), False)
		product = self.env['product.product'].browse(product_id) or self.product_id
		if product:
			for field in mapped_fields.keys():
				duration = getattr(product, mapped_fields[field])
				if duration:
					date = datetime.datetime.now() + datetime.timedelta(days=duration)
					res[field] = fields.Datetime.to_string(date)
		return res

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
		self.reserved_qty = sum(quants.mapped('reserved_quantity'))