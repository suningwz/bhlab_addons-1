# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat


class StockCardReportWizard(models.TransientModel):
    _name = 'stock.card.report.wizard'
    _description = 'Stock Card Report Wizard'

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Period',
    )
    date_from = fields.Date(
        string='Start Date',
    )
    date_to = fields.Date(
        string='End Date',
    )
    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Products',
        required=True,
    )

    @api.onchange('date_range_id')
    def _onchange_date_range_id(self):
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.model
    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or '0001-01-01'
        date_to = self.date_to or fields.Date.context_today(self)

        self._cr.execute("""
                SELECT move.date, move.product_id, stock_move_line.qty_done,
                    move.product_uom_qty, move.product_uom, move.reference,
                    move.location_id,move.location_dest_id,move.name,
                    move.partner_id,stock_move_line.ref,stock_move_line.expiry_date
                FROM stock_move move
                INNER JOIN stock_move_line on move.id = stock_move_line.move_id
				INNER JOIN stock_location on move.location_id = stock_location.id
                WHERE ((move.location_id ='15' and move.location_dest_id ='9') or (move.location_id ='13' and move.location_dest_id ='12') or (move.location_id ='9' and move.location_dest_id ='15'))
                    and move.state = 'done'
                    and move.product_id in %s
                    and move.date >= %s 
                    and move.date <= %s
                ORDER BY move.date, move.product_qty
            """,(tuple(self.product_ids.ids),date_from, date_to))

        stock_card_results = self._cr.dictfetchall()
        self.env['card.tree'].search([]).unlink()
        for line in stock_card_results:
            result = {
                'partner_id': line.get("partner_id"),
                'date': line.get("date"),
                'product_qty': line.get("qty_done"),
                'location_id':line.get("location_id"),
                'location_dest_id': line.get("location_dest_id"),
                'reference': line.get("reference"),
                'expiry_date': line.get("expiry_date"),
                'ref':line.get("ref"),
                }
            self.env['card.tree'].create(result)

    def button_export_tree(self):
        self.ensure_one()
        action = self.env.ref('stock_card_report.action_stock_card_tree')
        vals = action.read()[0]
        self._compute_results()
        return vals
