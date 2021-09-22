# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one('tender.contract', string='Contrat',readonly=True)
    lead_tender_id = fields.Many2one('crm.lead.tender', string='Appel d\'offre', readonly=True)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        for order in self:
            invoices = super(SaleOrder, self).action_invoice_create(grouped,final)
            if order.contract_id :  
                for invoice in invoices :
                    self.env['account.invoice'].browse(invoice).write({'contract_id': order.contract_id.id})
            return invoices
    
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    contract_line_id = fields.Many2one('contract.lines', string='Contrat line')
    
    @api.model
    def create(self, vals):
        _logger.warning('Begin create20')
        if vals.get('order_id',False) and vals.get('product_id',False):
            order = self.env['sale.order'].browse(vals.get('order_id',False))
            if order.contract_id : 
                for line in order.contract_id.contract_lines : 
                    if line.product_id.id == vals.get('product_id',False) :
                        vals['contract_line_id'] = line.id
                        break
            
    
        result = super(SaleOrderLine, self).create(vals)
        
        # if result and  result.order_id.contract_id and (result.is_reactif_dedie or result.is_reactif_manuel) :
        #     std = self.search([('id','!=',result.id),('related_line_id', '=', result.id)])
        #     for contract_line in result.order_id.contract_id.contract_lines : 
        #             if contract_line.product_id.id == std.product_id.id :
        #                 std.write({'contract_line_id' : contract_line.id})
        #                 break
        return result
    
    
    