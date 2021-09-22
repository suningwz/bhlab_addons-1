# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class GenerateContractWiz(models.TransientModel):
    _name = 'generate.contract.wiz'
    _description = 'Generate Contract Wizard'

    name = fields.Char('Contrat N°', required=True)
    begin_date = fields.Date(string='Date début', required=True)
    end_date = fields.Date(string='Date fin', required=True)
    signed_date = fields.Date(string='Date de signature')
    
    @api.one
    def action_generate_contract(self):
        leads = self.env['crm.lead.tender'].browse(self.env.context.get('active_ids'))
        for lead in leads :
            pricelist_vals = {'name':str(self.name) + " " + str(lead.partner_id.name), 'partner_id' : lead.partner_id.id}
            pricelist = self.env['product.pricelist'].create(pricelist_vals)
            lead.write({'pricelist_id':pricelist.id})
            vals = {'name':self.name,
                    'partner_id' : lead.partner_id.id,
                    'begin_date':self.begin_date,
                    'end_date':self.end_date,
                    'signed_date':self.signed_date,
                    'signed_date':self.signed_date,
                    'lead_id' : lead.id,
                    'pricelist_id' : pricelist.id,
                    'contract_type':lead.contract_type,
                    'contract_length' : lead.contract_length,
                    }
            contract = self.env['tender.contract'].create(vals)
            for line in lead.tender_line :
                if line.won_uom_qty > 0.0 :
                    
                    line_vals = {'tender_id':contract.id,
                                'name':line.name,
                                'sequence':line.sequence,
                                'price_unit':line.price_unit,
                                'price_subtotal':line.price_subtotal,
                                'price_tax':line.price_tax,
                                'price_total':line.price_total,
                                'price_reduce':line.price_reduce,
                                'price_reduce_taxinc':line.price_reduce_taxinc,
                                'price_reduce_taxexcl':line.price_reduce_taxexcl,
                                'discount':line.discount,
                                'product_id':line.product_id.id,
                                'product_updatable':line.product_updatable,
                                'product_uom_qty':line.won_uom_qty,
                                'product_uom':line.product_uom.id,
                                'salesman_id':line.salesman_id.id,
                                'company_id':line.company_id.id,
                                'currency_id':line.currency_id.id,
                                'order_partner_id':line.order_partner_id.id,
                                'display_type':line.display_type,
                                'state':'draft',
                                'order_partner_id':line.order_partner_id.id,
                                'tax_id': [[6, False, line.tax_id.ids]],
                                'invoicing':line.invoicing,
                                'pattern_not_invoicing':line.pattern_not_invoicing,
                                'is_reactif_dedie':line.is_reactif_dedie,
                                'is_reactif_manuel':line.is_reactif_manuel,
                                'standard_ids' : [[6, False, line.standard_ids.ids]],
                                'tender_line_id' : line.id,
                                }
                    
                    pricelist_item_vals = {
                                           'pricelist_id' : pricelist.id,
                                           'product_tmpl_id':line.product_id.product_tmpl_id.id,
                                           'product_uom':line.product_uom.id,
                                           'applied_on':'1_product',
                                           'base' :'list_price',
                                           'date_start':self.begin_date,
                                           'date_end':self.end_date,
                                           'compute_price' :'fixed',
                                           'fixed_price':line.price_unit,
                                           'note' :lead.name }
                    
                    self.env['contract.lines'].create(line_vals)
                    self.env['product.pricelist.item'].create(pricelist_item_vals)
                    
            # for contract_line in contract.contract_lines : 
            #     if contract_line.invoicing =='do_not_invoice' and contract_line.pattern_not_invoicing =='std' : 
            #         related_line = self.env['contract.lines'].search([('tender_line_id', '=', contract_line.tender_line_id.related_line_id.id)], limit =1)
            #         if related_line :
            #             contract_line.write({'related_line_id' : related_line.id})
        return True
