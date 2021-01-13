# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    availability_validation_control = fields.Boolean(string='Quantity available validation control')
    reservation_validation_control = fields.Boolean(string='Reservation quantity validation control')


class StockPicking(models.Model):
    _inherit = 'stock.picking'
  
    def button_validate(self):
        number = 1
        check_exipry_products = False
        line_str = ''
        for line in self.move_line_ids:
            line.number = number
            number += 1
        if self.picking_type_id.availability_validation_control:
            for line in self.move_line_ids:
                if (line.qty_done > line.available_qty) and (line.location_id == 'WH/Stock'):
                    _logger.warn("line.available_qty = %s , line.qty_done = %s",line.available_qty,line.qty_done)
                    _logger.warn("line.location_id = %s ",line.location_id)
                    raise UserError(
                        _("Quntity done is superior to quantity available"))
        if self.picking_type_id.reservation_validation_control:
            for line in self.move_line_ids:
                if (line.product_uom_qty != line.qty_done) and self.origin.find != "Retour":
                    _logger.warn("line.product_uom_qty = %s , line.qty_done = %s",line.product_uom_qty,line.qty_done)
                    raise UserError(
                        _("Quntity reserved is not equal to quantity done"))
        
        return super().button_validate()
