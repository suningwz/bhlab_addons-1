from odoo import api, fields, models, _


class ProductCard(models.TransientModel):
    _name = 'card.tree'
    _description = 'Stock Card tree'

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name='product.product')
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name='uom.uom')
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name='stock.location')
    location_dest_id = fields.Many2one(comodel_name='stock.location')
    partner_id = fields.Many2one('res.partner')
    ref = fields.Char()
    expiry_date = fields.Datetime()

    def open_stock_piking(self):
        id = self.env['stock.picking'].search([('name', '=', self.reference)]).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Movement',
            'target': 'new',
            'res_model': 'stock.picking',
            'res_id': id,
            'view_type': 'form',
            'views': [[False,'form']],
            'context': {},
        };