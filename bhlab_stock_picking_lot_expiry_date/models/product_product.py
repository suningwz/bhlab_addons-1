# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expiry_time = fields.Integer(string='Product Expiry Time',
        help='When a new a Serial Number is issued, this is the number of days before the goods may become dangerous and must not be consumed.')
