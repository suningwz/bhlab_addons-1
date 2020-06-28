# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	@api.multi
	def _create_picking(self):
		_logger.warn('none> PurchaseOrder._create_picking()')
		ret = super(PurchaseOrder, self)._create_picking()
		obj = self.env['stock.pack.operation.lot']
		for order in self:
			_logger.warn('\ninfo> po: %s', order)
			for line in order.order_line:
				_logger.warn('\n info> line: %s; move_ids: %s; pol_lot_ids: %s', line, line.move_ids, line.pol_lot_ids)
				if line.pol_lot_ids:
					for move in line.move_ids:
						_logger.warn('\n  info> move: %s; linked_move_operation_ids: %s', move, move.linked_move_operation_ids)
						for smol in move.linked_move_operation_ids:
							_logger.warn('\n   info> smol: %s; operation_id: %s; pol_lot_ids: %s', smol, smol.operation_id, line.pol_lot_ids)
							for pol_lot in line.pol_lot_ids:
								_logger.warn('\n    info> pol_lot: %s; lot_name: %s; qty: %s; expiry_date: %s', pol_lot, pol_lot.lot_name, pol_lot.qty, pol_lot.expiry_date,)
								obj.create({'operation_id': smol.operation_id.id, 'lot_name': pol_lot.lot_name, 'qty':pol_lot.qty, 'expiry_date':pol_lot.expiry_date})
		return ret
		
	@api.multi
	def button_confirm(self):
		for order in self:
			if order.state not in ['draft', 'sent']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			computed_validation_amount = self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id)
			_logger.warn('\nNone>po_double_validation: %s; po_double_validation_amount: %s; computed_validation_amount: %s; amount_total: %s;', order.company_id.po_double_validation, order.company_id.po_double_validation_amount, computed_validation_amount, order.amount_total)
			if order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < computed_validation_amount):#\
					#or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
		return True

	@api.depends('order_line')
	def _compute_is_really_shipped(self):
		for order in self:
			order.is_really_shipped = True
			for ol in order.order_line:
				if ol.qty_received < ol.product_qty:
					order.is_really_shipped = False
					break
			_logger.warn('\nNone>order.id: %s; is_really_shipped: %s;', order.id,order.is_really_shipped)

	is_really_shipped = fields.Boolean(compute="_compute_is_really_shipped")
	
class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"
	
	pol_lot_ids = fields.One2many('pol.operation.lot', 'pol_id', 'Lots/Serial Numbers Used')
	pol_lots_visible = fields.Boolean(compute='_compute_pol_lots_visible')
	
	@api.one
	def _compute_pol_lots_visible(self):
		_logger.warn('none> PurchaseOrderLine._compute_pol_lots_visible()')
		self.pol_lots_visible = self.product_id.tracking != 'none'
		_logger.warn('info> pol_lots_visible: %s', self.pol_lots_visible)
	
	@api.onchange('product_id')
	def onchange_product_id_warning(self):
		_logger.warn('none> PurchaseOrderLine.onchange_product_id_warning()')
		if not self.product_id:
			return
		self.pol_lots_visible = self.product_id.tracking != 'none'
		return super(PurchaseOrderLine, self).onchange_product_id_warning()
	

class POLOperationLot(models.Model):
	_name = "pol.operation.lot"
	_description = "Lot/Serial number for purchase order"

	pol_id = fields.Many2one('purchase.order.line')
	qty = fields.Float('Quantié', default=1.0, required=True)
	#lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
	lot_name = fields.Char('Lot/N° de série', required=True)
	expiry_date = fields.Date('Date de péremption', required=True)

	

		