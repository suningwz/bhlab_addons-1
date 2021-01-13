# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    expiry_date = fields.Datetime(related='lot_id.expiry_date', widget='Date')
    ref = fields.Char(string='Lot', related='lot_id.ref')
    available_qty = fields.Float(string='Qty availble', related='lot_id.available_qty',store=True)
    
    
    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'fefo':
            return 'removal_date ASC NULLS FIRST, id'
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)
