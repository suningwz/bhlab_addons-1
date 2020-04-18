# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	_name = 'exiry.config.settings'

	product_expiry_alert_time = fields.Integer(string='Product Expiry Alert Days', default=60, help='This is the number of days to alert before product expiry.')
	
	@api.multi
	def set_default_product_expiry_alert_time(self):
		if self.env.user._is_admin() or self.env['res.users'].has_group('stock.group_production_lot'):
			IrValues = self.env['ir.config_parameter'].sudo()
		else:
			IrValues = self.env['ir.values']
		IrValues.set_param('res.config.settings', 'product_expiry_alert_time', self.product_expiry_alert_time)
	