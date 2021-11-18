# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import UserError,Warning

import logging

_logger = logging.getLogger(__name__)


class LinkSelesOrderWiz(models.TransientModel):
    _name = 'link.sales.order.wiz'
    _description = 'Link Sales Order Wizard'

    order_ids = fields.Many2many(
        comodel_name='sale.order',
        string='Sales Orders',
        required=True,
    )

    def action_link_sales_order(self):
        _logger.warning("id --> " + str(self.env.context.get('active_ids')))
        contract_id = self.env['tender.contract']\
            .search([('id', 'in', self.env.context.get('active_ids'))])
        contract_line_id = self.env['tender.line'] \
            .search([('id', 'in', self.env.context.get('active_ids'))])
        _logger.warning("contract --> " + contract_id.name)
        for order_ctr in self.order_ids:
            if order_ctr.contract_id:
                message = _(
                    "The (%s) is already linked to contract named (%s) " % (order_ctr.name, order_ctr.contract_id.name))
                raise UserError(message)
            if order_ctr.invoice_status == 'invoiced' or order_ctr.invoice_status == 'no':
                message = _(
                    "The (%s) is already invoiced") % order_ctr.name
                raise UserError(message)

        for order in self.order_ids:
            _logger.warning("SOs --> " + order.name)
            order.write({'contract_id': contract_id.id})
            for line in contract_id.contract_lines:
                for order_line in order.order_line:
                    if line.product_id.id == order_line.product_id.id:
                        order.write({'contract_line_id': order_line.product_id.id})
        return
