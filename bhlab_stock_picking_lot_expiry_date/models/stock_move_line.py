# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from datetime import date, datetime, time
from odoo.exceptions import UserError

import logging 
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    

    ref = fields.Char(string='Lot', related='lot_id.ref',store=True, compute='_compute_upper')
    expiry_date = fields.Datetime(string="DLC", related='lot_id.expiry_date', store=True)
    available_qty = fields.Float(string='Qty availble', related='lot_id.available_qty',store=True)
    reserved_qty = fields.Float(string='Qty reserved', related='lot_id.reserved_qty',store=True)

    ref_name = fields.Char(string='Lot', store=True)
    expiry_date_name = fields.Datetime(string="DLC", store=True)