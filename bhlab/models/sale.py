# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.multi
	def action_confirm(self):
		_logger.warn('\nNone>SaleOrder.action_confirm()')
		for order in self:
			order.state = 'sale'
			order.confirmation_date = fields.Datetime.now()
			if self.env.context.get('send_email'):
				self.force_quotation_send()
			#order.order_line._action_procurement_create()
		#if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
		#    self.action_done()
		return True

	@api.multi
	def action_create_delivery(self):
		_logger.warn('\nNone>SaleOrder.action_create_delivery()')
		for order in self:
			#order.state = 'sale'
			#order.confirmation_date = fields.Datetime.now()
			#if self.env.context.get('send_email'):
			#    self.force_quotation_send()
			order.order_line._action_procurement_create()
		if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
			self.action_done()
		return True

	@api.depends('order_line')
	def _compute_is_really_shipped(self):
		_logger.warn('None> SaleOrder->_compute_is_really_shipped()')
		for order in self:
			_logger.warn('\ninfo>order.id: %s; is_really_shipped: %s;', order.id,order.is_really_shipped)
			order.is_really_shipped = True
			for ol in order.order_line:
				if ol.qty_delivered < ol.product_uom_qty:
					order.is_really_shipped = False
					break
			_logger.warn('\ninfo>order.id: %s; state: %s; invoice_status: %s; is_really_shipped: %s;', order.id, order.state, order.invoice_status, order.is_really_shipped)

	is_really_shipped = fields.Boolean(compute="_compute_is_really_shipped")		
	