# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.depends('invoice_line_ids')
	def _get_picking_names(self):
		_logger.warn('none>AccountInvoice._get_picking_names()')
		picking_names = ""
		picking_name_ids=[]
		il_has_lots = False
		if self.type == 'out_invoice' or self.type == 'in_refund':
			pick_type = 'outgoing'
		elif self.type == 'in_invoice' or self.type == 'out_refund':
			pick_type = 'incoming'
		_logger.warn('\ninfo>type: %s; look4pick_type: %s', type, pick_type)
		for il in self.invoice_line_ids:
			stock_moves = False
			if il.sale_line_ids:
				sol = il.sale_line_ids[0]
				if sol.procurement_ids:
					proc_order = sol.procurement_ids[0]
					stock_moves = proc_order.move_ids
			elif il.purchase_line_id:
				stock_moves = il.purchase_line_id.move_ids
			_logger.warn('\ninfo>il: %s; stock_moves: %s', il.id, stock_moves)
			if stock_moves:
				for i,sm in enumerate(stock_moves):
					if sm.lot_ids and len(sm.lot_ids) > 0:
						il_has_lots = True
					if sm.picking_type_id.code == pick_type and sm.state == 'done' and sm.picking_id.id not in picking_name_ids:
						picking_names += sm.picking_id.name + ", "
						picking_name_ids.append(sm.picking_id.id)
						#if i < len(stock_moves)-1:
						#	picking_names += ", "
				_logger.warn('\ninfo>picking_names: %s; il_has_lots: %s',picking_names,il_has_lots)			
				#return [picking_names,il_has_lots]
		if picking_names == "":
			return ["",il_has_lots]
		else:
			return [picking_names[:-2],il_has_lots]			
	

class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	@api.depends('sale_line_ids','purchase_line_id')
	def _has_lots(self):
		_logger.warn('none>AccountInvoiceLine._has_lots()')
		for il in self:
			if il.invoice_id.type == 'out_invoice' or il.invoice_id.type == 'in_refund':
				pick_type = 'outgoing'
			elif il.invoice_id.type == 'in_invoice' or il.invoice_id.type == 'out_refund':
				pick_type = 'incoming'
						
			_logger.warn('\ninfo>il.invoice_id.type: %s; look4pick_type: %s', il.invoice_id.type,pick_type)
			il.has_lots = False
			stock_moves = False
			if il.sale_line_ids:
				sol = il.sale_line_ids[0]
				if sol.procurement_ids:
					proc_order = sol.procurement_ids[0]
					stock_moves = proc_order.move_ids
			elif il.purchase_line_id:
				stock_moves = il.purchase_line_id.move_ids
			_logger.warn('\ninfo>stock_moves: %s', stock_moves)
			if stock_moves:
				for sm in stock_moves:
					if sm.picking_type_id.code == pick_type:
						il.quant_ids += sm.quant_ids
						if sm.lot_ids and len(sm.lot_ids) > 0:
							il.has_lots = True
				_logger.warn('\ninfo>quant_ids: %s', il.quant_ids)

	@api.depends('sale_line_ids','purchase_line_id')
	def _get_lots(self):
		_logger.warn('none>AccountInvoiceLine._get_lots()')
		res = {}
		for il in self:
			if il.invoice_id.type == 'out_invoice' or il.invoice_id.type == 'in_refund':
				pick_type = 'outgoing'
			elif il.invoice_id.type == 'in_invoice' or il.invoice_id.type == 'out_refund':
				pick_type = 'incoming'
			_logger.warn('\ninfo>il.invoice_id.type: %s; look4pick_type: %s', il.invoice_id.type,pick_type)
			
			stock_moves = False
			if il.sale_line_ids:
				sol = il.sale_line_ids[0]
				if sol.procurement_ids:
					proc_order = sol.procurement_ids[0]
					stock_moves = proc_order.move_ids
			elif il.purchase_line_id:
				stock_moves = il.purchase_line_id.move_ids
			_logger.warn('\ninfo>stock_moves: %s', stock_moves)
			if stock_moves:
				for sm in stock_moves:
					if sm.picking_type_id.code == pick_type:
						for q in sm.quant_ids:
							if res.has_key(q.lot_id.name):
								res[q.lot_id.name][2] += q.qty
							else:
								res[q.lot_id.name]=[q.lot_id.name, q.lot_id.expiry_date, q.qty]
						#il.quant_ids += sm.quant_ids
						if sm.lot_ids and len(sm.lot_ids) > 0:
							il.has_lots = True
				_logger.warn('\ninfo>res: %s', res)
		return res
	
	has_lots = fields.Boolean(compute='_has_lots')
	quant_ids = fields.Many2many('stock.quant', compute='_has_lots')
	