# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	product_expiry_alert_time = fields.Integer(string='Product Expiry Alert Days', default=60, help='This is the number of days to alert before product expiry.')

	@api.multi
	def set_values(self):
		if self.env.user._is_admin() or self.env['res.users'].has_group('stock.group_production_lot'):
			res = super(StockConfigSettings, self).set_values()
			param = self.env['ir.config_parameter'].sudo()
			param.set_param('product_expiry_alert_time.product_expiry_alert_time',self.product_expiry_alert_time)
			return res

	@api.model
	def get_values(self):
		res = super(StockConfigSettings, self).get_values()
		param = self.env['ir.config_parameter'].sudo()
		product_expiry_alert_time = int(param.get_param('product_expiry_alert_time.product_expiry_alert_time'))
		res.update(
			product_expiry_alert_time = product_expiry_alert_time
		)
		return res
