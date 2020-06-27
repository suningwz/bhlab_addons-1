# -*- coding: utf-8 -*-

import time
from lxml import etree
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
	_inherit = 'stock.move'

	@api.multi
	def action_set_draft(self):
		""" Cancels the moves and if all moves are cancelled it cancels the picking. """
		# TDE DUMB: why is cancel_procuremetn in ctx we do quite nothing ?? like not updating the move ??
		_logger.warn('none> StockMove.action_set_draft()')
		if any(move.state == 'done' for move in self):
			raise UserError(_('You cannot set to Draft a stock move that has been set to \'Done\'.'))

		procurements = self.env['procurement.order']
		_logger.warn('info> self: %s;',self)
		for move in self:
			_logger.warn('info> move_id: %s; state: %s; reserved_quant_ids: %s; move_dest_id: %s; procurement_id: %s; propagate: %s;',move.id, move.state, move.reserved_quant_ids, move.move_dest_id, move.procurement_id, move.propagate)
			if move.reserved_quant_ids:
				move.quants_unreserve()
			if self.env.context.get('cancel_procurement'):
				if move.propagate:
					pass
					# procurements.search([('move_dest_id', '=', move.id)]).cancel()
			else:
				if move.move_dest_id:
					if move.propagate:
						move.move_dest_id.action_set_draft()
					elif move.move_dest_id.state == 'waiting':
						# If waiting, the chain will be broken and we are not sure if we can still wait for it (=> could take from stock instead)
						move.move_dest_id.write({'state': 'confirmed'})
				if move.procurement_id:
					procurements |= move.procurement_id

		self.write({'state': 'draft', 'move_dest_id': False})
		if procurements:
			procurements.check()
		return True

class StockBackorderConfirmation(models.TransientModel):
	_inherit = 'stock.backorder.confirmation'

	@api.multi
	def process(self):
		_logger.warn('none> StockBackorderConfirmation.process()')
		super(StockBackorderConfirmation, self).process()
		backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', self.pick_id.id)])
		backorder_pick.action_set_draft()
	
class StockPicking(models.Model):
	_inherit = 'stock.picking'
	
	is_return_picking = fields.Boolean('Is a Return Picking', default=False, readonly=True)
				
	@api.multi
	def action_set_draft(self):
		_logger.warn('none> StockPicking.action_set_draft()')
		self.mapped('move_lines').action_set_draft()
		return True

	@api.multi
	def action_confirm(self):
		_logger.warn('none> StockPicking.action_confirm()')
		for picking in self:
			_logger.warn('info> picking: %s; name: %s',picking.id, picking.name)
			if picking.backorder_id and picking.name[0]=='#':
				name = picking.picking_type_id.sequence_id.next_by_id()
				_logger.warn('info> new name: %s;',name)
				picking.write({'name':name})
				
		return super(StockPicking, self).action_confirm()

	@api.multi
	def do_new_transfer(self):
		_logger.warn('none> StockPicking.do_new_transfer()')
		for picking in self:
			_logger.warn('info> picking: %s; name: %s',picking.id, picking.name)
			if picking.backorder_id and picking.name[0]=='#':
				name = picking.picking_type_id.sequence_id.next_by_id()
				_logger.warn('info> new name: %s;',name)
				picking.write({'name':name})
		
		return super(StockPicking, self).do_new_transfer()
		
	@api.multi
	def _create_backorder(self, backorder_moves=[]):
		""" Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
		"""
		# TDE note: o2o conversion, todo multi
		_logger.warn('none> StockPicking._create_backorder()')
		backorders = self.env['stock.picking']
		for picking in self:
			backorder_moves = backorder_moves or picking.move_lines
			if self._context.get('do_only_split'):
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
			else:
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
			if not not_done_bo_moves:
				continue
			backorder_picking = picking.copy({
				'name': '<'+picking.name,
				'move_lines': [],
				'pack_operation_ids': [],
				'backorder_id': picking.id
			})
			backorder_picking.write({'name':'#'+str(backorder_picking.id)})

			picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
			not_done_bo_moves.write({'picking_id': backorder_picking.id})
			if not picking.date_done:
				picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
			#backorder_picking.action_confirm()
			#backorder_picking.action_assign()
			backorders |= backorder_picking
		return backorders

class ReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'
	
	@api.multi
	def create_returns(self):
		_logger.warn('none> ReturnPicking.create_returns()')
		ret = super(ReturnPicking, self).create_returns()
		_logger.warn('\ninfo> ret: %s', ret)
		self.env['stock.picking'].browse(ret['res_id']).write({'is_return_picking':True})
		return ret
	
class PackOperation(models.Model):
	_inherit = "stock.pack.operation"

	def _compute_lpm_lot_domain(self):
		_logger.warn('none> PackOperation._compute_lpm_lot_domain()')
		_logger.warn('\ninfo> picking_id.picking_type_code: %s; picking_id.is_return_picking: %s', self.picking_id.picking_type_code, self.picking_id.is_return_picking)
		lot_domain_ids = []
		if self.picking_id.is_return_picking:
			if self.picking_id.picking_type_code == 'outgoing':
				orm_obj = self.env['purchase.order']
				procurement_group_id = 'group_id'
			elif self.picking_id.picking_type_code == 'incoming':
				orm_obj = self.env['sale.order']
				procurement_group_id = 'procurement_group_id'
			so_po_search = orm_obj.search([(procurement_group_id,'=',self.picking_id.group_id.id)])
			_logger.warn('\ninfo> orm_obj: %s; so_po_search:%s', orm_obj, so_po_search)			
			if so_po_search:
				for sp in so_po_search.picking_ids:
					for spo in sp.pack_operation_ids:
						for pl in spo.pack_lot_ids:
							if pl.lot_id:
								lot_domain_ids.append(pl.lot_id.id)
		else:
			datenow = fields.Date.context_today(self)
			search_not_expired = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id),('expiry_date','>',datenow)])
			_logger.warn('\ninfo> datenow: %s; search_not_expired: %s', datenow, search_not_expired)
			lot_domain_ids = search_not_expired.ids
		
		_logger.warn('\ninfo> lot_domain_ids: %s', lot_domain_ids)
		return lot_domain_ids

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		_logger.warn('none> PackOperation.fields_view_get()')
		res = super(PackOperation, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		_logger.warn("\ninfo> yo man !")
		if self._context.get('lot_domain_ids'):
			#_logger.warn("\ninfo> res['fields']['pack_lot_ids']:\n%s", res['fields']['pack_lot_ids'])
			res_lot_id = res['fields']['pack_lot_ids']['views']['tree']['fields']['lot_id']
			res_lot_id['domain'] = [('id', 'in', self._context['lot_domain_ids'])]
			_logger.warn("\nINFO> res_lot_id:\n%s", res_lot_id)			
		return res

	@api.multi
	def action_split_lots(self):
		_logger.warn('none> PackOperation.action_split_lots()')
		_logger.warn('\ninfo> state: %s; context: %s', self.state, self.env.context)
		ret = super(PackOperation, self).action_split_lots()
		if ret['context']['only_create'] == False:
			lot_domain = self._compute_lpm_lot_domain()
			ret['context'].update({'lot_domain_ids': lot_domain})
		_logger.warn('\ninfo> super: %s', ret)
		return ret
	split_lot2 = action_split_lots
		

class PackOperationLot(models.Model):
	_inherit = "stock.pack.operation.lot"

	expiry_date = fields.Date(string='Expiry Date')
	expiry_date_rel = fields.Date(related='lot_id.expiry_date',string='Lot Expiry Date')
	
	@api.multi
	def write(self, values):
		_logger.warn('none> PackOperationLot.write()')
		ret = super(PackOperationLot, self).write(values)
		if values.has_key('lot_id'):
			_logger.warn('info> self.expiry_date: %s; self.lot_id.expiry_date: %s;',self.expiry_date, self.lot_id.expiry_date)
			if self.expiry_date:
				self.lot_id.write({'expiry_date':self.expiry_date})
		return ret
				