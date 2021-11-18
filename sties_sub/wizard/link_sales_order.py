# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
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
        _logger.warning("contract --> " + contract_id.name)
        for order_ctr in self.order_ids:
            if order_ctr.contract_id:
                title = _("Warning for %s") % order_ctr.name
                message = _(
                    "The %s is already linked to contract") % order_ctr.name
                warning = {
                    'title': title,
                    'message': message
                }
                return {'warning': warning}
            if order_ctr.invoice_status == 'invoiced' or order_ctr.invoice_status == 'no':
                title = _("Warning for %s") % order_ctr.name
                message = _(
                    "The %s is already invoiced") % order_ctr.name
                warning = {
                    'title': title,
                    'message': message
                }
                return {'warning': warning}

        for order in self.order_ids:
            _logger.warning("SOs --> " + order.name)
            order.write({'contract_id': contract_id.id})
            for line in order.contract_id.contract_lines:
                for product in order.order_line:
                    if line.id == product.id:
                        order.write({'contract_line_id': line.id})
        return
