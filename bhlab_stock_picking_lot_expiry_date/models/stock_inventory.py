# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import exceptions, fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class StockInventory(models.Model):
    _inherit = 'stock.inventory.line'

    expiry_date = fields.Datetime(related='prod_lot_id.expiry_date', widget='Date')
    ref = fields.Char(string='Lot', related='prod_lot_id.ref')
    available_qty = fields.Float(string='Qty availble', related='prod_lot_id.available_qty',store=True)