# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

   #  @api.multi
   #  @api.constrains('order_line')
   #  def _check_exist_product_in_line(self):
   #    for purchase in self:
   #        exist_product_list = []
   #        for line in purchase.order_line:
   #           if line.product_id.id in exist_product_list:
   #              raise ValidationError(_('Product should be one per line.'))
   #           exist_product_list.append(line.product_id.id)