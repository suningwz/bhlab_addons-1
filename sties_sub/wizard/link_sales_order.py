# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class LinkSelesOrderWiz(models.TransientModel):
    _name = 'link.sales.order.wiz'
    _description = 'Link Sales Order Wizard'

    sales_order_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Orders',
        required=True,
    )

    @api.one
    def action_link_sales_order(self):
        return
