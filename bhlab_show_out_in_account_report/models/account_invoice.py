##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice'

    num_picking = fields.Char(compute = '_find_picking_number', store=True)

    @api.depends('move_id', 'move_id.stock_move_id', 'move_id.stock_move_id.picking_id')
    def _find_picking_number(self):
        for line in self:
            line.num_picking = line.move_id.stock_move_id.picking_id.name if line.move_id and line.move_id.stock_move_id else False
