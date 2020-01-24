# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    @api.constrains('move_line_ids_without_package')
    def _check_exist_product_in_line(self):
      for picking in self:
          exist_product_list = []
          exist_lot_list = []
          exist_expiry_date_list = []
          for line in picking.move_line_ids_without_package:
             if line.product_id.id in exist_product_list and line.ref in exist_lot_list and line.expiry_date in exist_expiry_date_list:
                raise ValidationError(_('Product should be one per line.'))
             exist_product_list.append(line.product_id.id)
             exist_lot_list.append(line.ref)
             exist_expiry_date_list.append(line.expiry_date)