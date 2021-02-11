# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
_logger = logging.getLogger(__name__)

try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')


class ImportTransfert(models.TransientModel):
	_name = 'import.transferts'
	_description = 'Import transferts'

	file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='File Type', default='CSV')
	file = fields.Binary(string="Upload File")
	location_id = fields.Many2one(comodel_name='stock.location' , required=True)
	location_dest_id = fields.Many2one(comodel_name='stock.location' , required=True)
	picking_type_id = fields.Many2one('stock.picking.type', "Operation Type", required=True)
	partner_id = fields.Many2one('res.partner', string='Partner')

	@api.multi
	def open_wizard(self):
		view = self.env.ref('bhlab_import_internal_transfer.import_transfert_form_view')
		#wiz = self.env['stock.picking'].create({})
		# TDE FIXME: a return in a loop, what a good idea. Really.
		return {
			'name': _('Import transfert'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.picking',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			#'res_id': wiz.id,
			'context': self.env.context,
		}

	@api.multi
	def import_transfert(self):
		if not self.file:
			raise ValidationError(_("Please Upload File to Import Products !"))
		pick_line_values = []
		pick_lines = []
		if self.file_type == 'CSV':
			line = keys = ['product_name', 'initial_demande']
			try:
				csv_data = base64.b64decode(self.file)
				data_file = io.StringIO(csv_data.decode("utf-8"))
				data_file.seek(0)
				file_reader = []
				csv_reader = csv.reader(data_file, delimiter=',')
				file_reader.extend(csv_reader)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))
			values = {}
			for i in range(len(file_reader)):
				field = list(map(str, file_reader[i]))
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						pick_line_values = self._get_move(values)
						pick_lines.append((0, 0, pick_line_values))
		else:
			try:
				file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
				file.write(binascii.a2b_base64(self.file))
				file.seek(0)
				values = {}
				workbook = xlrd.open_workbook(file.name)
				sheet = workbook.sheet_by_index(0)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))

			for row_no in range(sheet.nrows):
				val = {}
				if row_no <= 0:
					fields = list(map(lambda row: str(row.value).encode('utf-8'), sheet.row(row_no)))
				else:
					line = list(map(
						lambda row: isinstance(row.value, bytes) and str(row.value).encode('utf-8') or str(row.value),
						sheet.row(row_no)))
					values.update({
						'product_name': line[0],
						'initial_demande': line[1],
					})
					pick_line_values = self._get_move(values)
					pick_lines.append((0, 0, pick_line_values))
		self.action_approve(pick_lines)


	def _get_move(self,values):
		product_external_id = values.get('product_name')
		initial_demande = values.get('initial_demande')
		product_id = self.env.ref(product_external_id)
		return{
				'product_id': product_id.id,
				'product_uom': product_id.uom_id.id,
				'product_uom_qty': initial_demande,
				'qty_done': 0.0,
				'name': product_id.name,
			}

	@api.multi
	def action_approve(self,pick_lines):
		for record in self:
			picking = {
				'partner_id': self.partner_id.id,
				'location_id': self.location_id.id,
				'location_dest_id': self.location_dest_id.id,
				'move_type': 'direct',
				'picking_type_id': self.picking_type_id.id,
				'ctsrf': record.id,
				'move_lines': pick_lines,
			}
			transfer = self.env['stock.picking'].sudo().create(picking)
			if transfer:
				record.state = 'approved'
				record.approved_date = fields.Datetime.now()
				record.approved_by = self.env.uid
			else:
				raise ValidationError(_("Something went wrong during your Request generation"))
		return True