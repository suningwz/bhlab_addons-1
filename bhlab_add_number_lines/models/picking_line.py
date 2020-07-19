from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'stock.move.line'

    number = fields.Integer(string="Nbr", store=True, default = 1)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    number = fields.Integer(string="Nbr" ,compute='_compute_get_number', store=True)

    @api.multi
    @api.constrains('move_line_ids_without_package')
    def _compute_get_number(self):
        for picking in self:
            number = 1
            _logger.warn('number = %s', number)
            for line in picking.move_line_ids_without_package:
                line.number = number
                number += 1
                _logger.warn('line number = %s', number)