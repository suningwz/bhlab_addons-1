# ?? 2018 Eficent (https://www.eficent.com)
# @author Jordi Ballester <jordi.ballester@eficent.com.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_stock_quantity_not_reserved = fields.Boolean(
        string='is stock quantity not reserved ?',
        help="Allow show quantity stock levels for the stockable products "
        "attached to this location.")