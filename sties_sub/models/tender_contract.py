# -*- coding: utf-8 -*-
# Part of Sties. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp
from werkzeug.urls import url_encode
import logging
_logger = logging.getLogger(__name__)

class TenderContract(models.Model):
    _name = "tender.contract"
    _description = "Tender contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.depends('contract_lines.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.contract_lines:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })
            
    active = fields.Boolean('Active', default=True, track_visibility=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange', default=lambda self: self.env.user)
    description = fields.Text('Notes')
    name = fields.Char('Contract N°', required=True, index=True)
    partner_id = fields.Many2one('res.partner', required = True,string='Customer', track_visibility='onchange', track_sequence=1, index=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('running', 'En cours'),
        ('done', 'Ctôturé'),
        ('suspended', 'Suspendu'),
        ('cancel', 'Annulé'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    contract_lines = fields.One2many('contract.lines', 'tender_id', string='Participations')
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Currency", required=True)
    amount_untaxed = fields.Monetary(string='Montant HT', store=True, readonly=True, compute='_amount_all', track_visibility='onchange', track_sequence=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always', track_sequence=6)
    begin_date = fields.Date(string='Begin date', required=True)
    end_date = fields.Date(string='Closed date', required=True)
    signed_date = fields.Date(string='Date de signature', readonly=True, states={'draft': [('readonly', False)]})
    lead_id = fields.Many2one('crm.lead.tender', string='Appel d\'offre', readonly=True, track_visibility='onchange', track_sequence=1, index=True)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    sale_number = fields.Integer(compute='_compute_sale_amount_total', string="Number of Quotations")
    order_ids = fields.One2many('sale.order', 'contract_id', string='Orders',readonly=True)
    invoice_ids = fields.One2many('account.invoice', 'contract_id', string='Factures',readonly=True)
    contract_extra_lines = fields.One2many('contract.extra.lines', 'tender_id', string='Participations', readonly=True)

    amount_total_contract_to_invoice = fields.Monetary(string='Total à facturer ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_contract_invoiced = fields.Monetary(string='Total facturé ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_contract_follow = fields.Monetary(string='Total encours ', store=False, readonly=True, compute='_amount_all_contract_values', track_visibility='always', track_sequence=6)
    percentage_of_target = fields.Float(compute='_amount_all_contract_values', string='Objectif(%)', store=True, readonly=True)
    
    amount_total_hors_contract_to_invoice = fields.Monetary(string='Total à facturer ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_hors_contract_invoiced = fields.Monetary(string='Total facturé ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_hors_contract_follow = fields.Monetary(string='Total encours ', store=False, readonly=True, compute='_amount_all_contract_values', track_visibility='always', track_sequence=6)
    
    amount_total_to_invoice = fields.Monetary(string='Total à facturer ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_invoiced = fields.Monetary(string='Total facturé ', store=False, readonly=True, compute='_amount_all_contract_values')
    amount_total_follow = fields.Monetary(string='Total encours ', store=False, readonly=True, compute='_amount_all_contract_values', track_visibility='always', track_sequence=6)
    global_percentage_of_target = fields.Float(compute='_amount_all_contract_values', string='Objectif(%)', store=True, readonly=True)
       
    contract_type = fields.Selection([
        ('ao_sale', 'Vente'),
        ('ao_mad', 'MAD'),
        ('prived_mad', 'MAD PRIVE'),
        ('consultation', 'Consultation'),
        ], string='Type du contrat ', required=True)
    
    
    contract_length = fields.Selection([
        ('1', '3 mois'),
        ('2', '6 mois'),
        ('3', '1 an'),
        ('4', '2 ans'),
        ('5', '3 ans'),
        ('6', '4 ans'),        
        ('7', '5 ans')   
        
        ], string='Durée du contrat')

    blocked = fields.Boolean(compute='_compute_blocked', string="Contrat bloqué")
               
    def _compute_blocked(self):
        for contract in self:
            contract.blocked = False
            if contract.amount_total_follow >= contract.amount_total : 
                contract.blocked = True
                
                                        
    @api.depends('contract_lines.qty_delivered','contract_lines.qty_invoiced','contract_extra_lines','contract_lines.subtotal_invoiced','contract_lines.subtotal_to_invoice')
    def _amount_all_contract_values(self):
        for contract in self:
            amount_total_to_invoice_hors =  0.0
            amount_total_invoiced_hors =  0.0
            for extra_line in contract.contract_extra_lines :
                amount_total_to_invoice_hors += extra_line.price_reduce_taxinc * extra_line.qty_to_invoice
                amount_total_invoiced_hors   += extra_line.price_reduce_taxinc * extra_line.qty_invoiced
            
            
            amount_total_invoiced =  0.0
            amount_total_to_invoice =  0.0
            for invoice in contract.invoice_ids.filtered(lambda inv: inv.state !='cancel'): 
                amount_total_invoiced += (invoice.amount_total - invoice.tax_stamp_amount) 
            for contract_line in contract.contract_lines:
                for line in contract_line.order_line.filtered(lambda ln: ln.invoice_status =='to invoice'):
                    amount_total_to_invoice += line.price_reduce_taxinc * line.qty_to_invoice
            
            contract.update({
                'amount_total_hors_contract_to_invoice': amount_total_to_invoice_hors,
                'amount_total_hors_contract_invoiced': amount_total_invoiced_hors,
                'amount_total_hors_contract_follow': amount_total_to_invoice_hors + amount_total_invoiced_hors, 
                
                'amount_total_contract_to_invoice': amount_total_to_invoice,
                'amount_total_contract_invoiced': amount_total_invoiced - amount_total_invoiced_hors,
                'amount_total_contract_follow': amount_total_invoiced - amount_total_invoiced_hors + amount_total_to_invoice, 
                'percentage_of_target' :   100*(amount_total_invoiced - amount_total_invoiced_hors + amount_total_to_invoice)/ contract.amount_total if contract.amount_total >0.0 else 0.0,
                
                'amount_total_to_invoice': amount_total_to_invoice_hors + amount_total_to_invoice,
                'amount_total_invoiced': amount_total_invoiced,
                'amount_total_follow':               amount_total_to_invoice_hors + amount_total_to_invoice + amount_total_invoiced,
                'global_percentage_of_target' : 100*(amount_total_to_invoice_hors + amount_total_to_invoice + amount_total_invoiced)/ contract.amount_total if contract.amount_total >0.0 else 0.0
       
            })
            
                        
    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', 'The name of the contract must be unique per company !')
    ]

    def _compute_sale_amount_total(self):
        for contract in self:
            nbr = 0
            for order in contract.order_ids:
                if order.state !='cancel' :
                    nbr += 1
            contract.sale_number = nbr
         
    @api.multi
    def copy_data(self, default=None):
        if not self.contract_type == 'prived_mad' :
            raise UserError(_('Il n\'est pas possible de dupliquer le contrat, veuillez créer un nouveau'))
        default = dict(default or {}, name=_("%s (Copy)") % self.name)
        if 'contract_lines' not in default:
            default['contract_lines'] = [(0, 0, line.copy_data()[0]) for line in self.contract_lines.filtered(lambda l: l.pattern_not_invoicing !='std')]
        return super(TenderContract, self).copy_data(default=default)
 
    
    @api.multi
    def unlink(self):
        for contract in self:
            if  contract.state not in ('draft', 'cancel'):
                raise UserError(_('Vous ne pouvez supprimer que les contrats à l\'état brouillon ou annulé.'))
        return super(TenderContract, self).unlink()
    
    @api.onchange('begin_date')
    def _onchange_begin_date(self):
        res = {}
        if (self.begin_date and self.end_date and self.end_date <= self.begin_date):
            self.begin_date = ''
            res['warning'] = {
                'title': _('La date demandée est incorrecte.'),
                'message': _("La date début du contrat est ultérieure ou égale à la date fin.")
            }
        return res    
    
    @api.onchange('end_date')
    def _onchange_end_date(self):
        res = {}
        if (self.end_date and self.begin_date and self.end_date <= self.begin_date):
            self.end_date = ''
            res['warning'] = {
                'title': _('La date demandée est incorrecte.'),
                'message': _("La date fin du contrat est antérieure ou égale à la date début.")
            }
        return res 
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        values = {}
        if self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id
        values['user_id'] = self.partner_id.user_id.id or self.partner_id.commercial_partner_id.user_id.id or self.env.uid
        self.update(values)
        
    @api.multi
    def action_confirm(self):
        for lead in self:
            if not lead.contract_lines :
                raise UserError(_('Veuillez ajouter au moins une ligne au contrat'))
            lead.write({'state': 'confirmed'})
            for line in lead.contract_lines:
                line.write({'state': 'confirmed'})
            
    @api.multi
    def action_running(self):
        for lead in self:
            lead.write({'state': 'running'})
            for line in lead.contract_lines:
                line.write({'state': 'running'})
                
    @api.multi
    def action_done(self):
        for lead in self:
            lead.write({'state': 'done'})
            for line in lead.contract_lines:
                line.write({'state': 'done'})
                
    @api.multi
    def action_suspended(self):
        for lead in self:
            lead.write({'state': 'suspended'})
            for line in lead.contract_lines:
                line.write({'state': 'suspended'})
            
    @api.multi
    def action_cancel(self):
        for contract in self:
            contract.write({'state': 'cancel'})
            for line in contract.contract_lines:
                line.write({'state': 'cancel'})
            
    def action_generate_extra_lines(self):
        self.contract_extra_lines.unlink()
        for order in self.order_ids :
            for line in order.order_line.filtered(lambda so: so.state != 'cancel') :
                if not line.contract_line_id :
                    line_vals = {'tender_id':self.id,
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
                                'product_uom_qty':line.product_uom_qty,
                                'product_uom':line.product_uom.id,
                                'untaxed_amount_invoiced':line.qty_invoiced * line.price_reduce_taxexcl,                            
                                'untaxed_amount_to_invoice':line.qty_to_invoice * line.price_reduce_taxexcl,
                                'subtotal_encours' : line.qty_invoiced * line.price_reduce_taxexcl + line.qty_to_invoice * line.price_reduce_taxexcl,     
                                'salesman_id':line.salesman_id.id,
                                'company_id':line.company_id.id,
                                'currency_id':line.currency_id.id,
                                'order_partner_id':line.order_partner_id.id,
                                'display_type':line.display_type,
                                'order_partner_id':line.order_partner_id.id,
                                'order_id':line.order_id.id,
                                'qty_delivered':line.qty_delivered,
                                'qty_invoiced':line.qty_invoiced,
                                'qty_to_invoice':line.qty_to_invoice,
                                'tax_id': [[6, False, line.tax_id.ids]],
                                }
                    self.env['contract.extra.lines'].create(line_vals)
                    
                    
    def generate_pricelist(self):
        for contract in self:
            pricelist_vals = {'name':str(contract.name), 'partner_id' : contract.partner_id.id}
            pricelist = self.env['product.pricelist'].create(pricelist_vals)
            contract.write({'pricelist_id':pricelist.id})
            for line in contract.contract_lines.filtered(lambda l: l.invoicing == 'to_invoice'):           
                pricelist_item_vals = {'pricelist_id' : pricelist.id,
                                       'product_tmpl_id':line.product_id.product_tmpl_id.id,
                                       'product_uom':line.product_uom.id,
                                       'applied_on':'1_product',
                                       'base' :'list_price',
                                       'date_start':self.begin_date,
                                       'date_end':self.end_date,
                                       'compute_price' :'fixed',
                                       'fixed_price':line.price_unit,
                                       'note' :contract.name
                                       }
                
                self.env['product.pricelist.item'].create(pricelist_item_vals)
    
class ContractLines(models.Model):
    _name = 'contract.lines'
    _description = "Tender contract Line"
    _order = 'tender_id, sequence, id'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the cintract line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.tender_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.tender_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('order_line','tender_id.order_ids','order_line.qty_invoiced')
    def _get_invoice_qty(self):
        for contract_line in self:
            qty = 0.0
            for order_line in contract_line.order_line : 
                qty += order_line.qty_invoiced
            contract_line.qty_invoiced = qty
            
    
    @api.depends('tender_id.order_ids','order_line','order_line.qty_invoiced','order_line.qty_to_invoice','order_line.invoice_lines') # ==/ HT
    def _get_subtotal_values(self):
        for contract_line in self:
            amount_taxexcl_invoiced = 0.0
            amount_taxexcl_to_invoice = 0.0
            for order_line in contract_line.order_line : 
                amount_taxexcl_invoiced   += order_line.price_reduce_taxexcl * order_line.qty_invoiced
                amount_taxexcl_to_invoice += order_line.price_reduce_taxexcl * order_line.qty_to_invoice
            contract_line.subtotal_invoiced = amount_taxexcl_invoiced
            contract_line.subtotal_to_invoice = amount_taxexcl_to_invoice         
            contract_line.subtotal_encours = amount_taxexcl_invoiced + amount_taxexcl_to_invoice
            contract_line.percentage_of_target = 100*(amount_taxexcl_invoiced + amount_taxexcl_to_invoice)/ contract_line.price_subtotal if contract_line.price_subtotal > 0.0 else 0.0

    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.depends('price_total', 'product_uom_qty')
    def _get_price_reduce_tax(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_subtotal', 'product_uom_qty')
    def _get_price_reduce_notax(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.tender_id.partner_id.property_account_position_id
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.tender_id.partner_id) if fpos else taxes

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        return {}

    @api.model
    def _prepare_add_missing_fields(self, values):
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('tender_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        vals_ls=[]
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))
        
        for vals in vals_list: 
            _logger.error('vals %s',vals)
            if vals.get('tender_id',False) and self.env['tender.contract'].browse(vals.get('tender_id',False)).contract_type == 'prived_mad' :
                if vals.get('is_reactif_dedie',False) or vals.get('is_reactif_manuel',False):
                    template_obj = self.env['product.template']
                    reactif_obj = template_obj.browse(vals.get('product_id',False))
                    vals['standard_ids']= [(6,0,reactif_obj.standard_ids.ids)]
            vals_ls.append(vals)    
    
        lines = super().create(vals_ls)
        
        for line in lines:
            if line.tender_id.contract_type == 'prived_mad' :
                if line.is_reactif_dedie or line.is_reactif_manuel :
                    for std in reactif_obj.standard_ids :
                        product = self.env['product.product'].search([('product_tmpl_id','=',std.id)])
                        standard_vals  = {'display_type': False, 
                                          'sequence': 9, 
                                          'product_uom_qty': line.product_uom_qty,
                                          'price_unit': 0, 
                                          'discount': 0, 
                                          'product_packaging': False, 
                                          'product_id': product.id, 
                                          'product_uom': product.uom_id.id,
                                          'tax_id': [[6, False, []]], 
                                          'name': self.get_sale_order_line_multiline_description_sale(product), 
                                          'tender_id': line.tender_id.id,
                                          'invoicing':'do_not_invoice',
                                          'pattern_not_invoicing':'std',
                                          'related_line_id' :line.id} 
                        super().create(standard_vals)
        
        return lines
    
    _sql_constraints = [
        ('accountable_required_fields',
            "CHECK(display_type IS NOT NULL OR (product_id IS NOT NULL AND product_uom IS NOT NULL))",
            "Missing required fields on accountable sale order line."),
        ('non_accountable_null_fields',
            "CHECK(display_type IS NULL OR (product_id IS NULL AND price_unit = 0 AND product_uom_qty = 0 AND product_uom IS NULL))",
            "Forbidden values on non-accountable sale order line"),
    ]

    def _update_line_quantity(self, values):
        orders = self.mapped('tender_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.tender_id == order)
            msg = "<b>The ordered quantity has been updated.</b><ul>"
            for line in order_lines:
                msg += "<li> %s:" % (line.product_id.display_name,)
                msg += "<br/>" + _("Ordered Quantity") + ": %s -> %s <br/>" % (
                line.product_uom_qty, float(values['product_uom_qty']),)
                if line.product_id.type in ('consu', 'product'):
                    msg += _("Delivered Quantity") + ": %s <br/>" % (line.qty_delivered,)
                msg += _("Invoiced Quantity") + ": %s <br/>" % (line.qty_invoiced,)
            msg += "</ul>"
            order.message_post(body=msg)

    @api.multi
    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError("You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type.")

        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) != 0)._update_line_quantity(values)

        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('tender_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(ContractLines, self).write(values)
        return result

    tender_id = fields.Many2one('tender.contract', string='Contrat', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits=dp.get_precision('Product Price'), readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    product_uom_qty = fields.Float(string='Qté du contrat', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered_all', 
                                  compute_sudo=True, store=True, digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    qty_invoiced = fields.Float(
        compute='_get_invoice_qty', string='Invoiced Quantity', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    
    subtotal_invoiced = fields.Float(
        compute='_get_subtotal_values', string='Montant facturé', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    
    subtotal_to_invoice = fields.Float(
        compute='_get_subtotal_values', string='Montant à facturer', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    
    subtotal_encours = fields.Float(
        compute='_get_subtotal_values', string='Montant encours', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    
    percentage_of_target = fields.Float(
        compute='_get_subtotal_values', string='Objectif', store=True, readonly=True)
    
    untaxed_amount_invoiced = fields.Monetary("Untaxed Invoiced Amount", compute='_compute_untaxed_amount_invoiced', compute_sudo=True, store=True)
    untaxed_amount_to_invoice = fields.Monetary("Untaxed Amount To Invoice", compute='_compute_untaxed_amount_to_invoice', compute_sudo=True, store=True)
    salesman_id = fields.Many2one(related='tender_id.user_id', store=True, string='Salesperson', readonly=True)
    company_id = fields.Many2one(related='tender_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    order_partner_id = fields.Many2one(related='tender_id.partner_id', store=True, string='Customer', readonly=False)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('running', 'En cours'),
        ('done', 'Ctôturé'),
        ('suspended', 'Suspendu'),
        ('cancel', 'Annulé'),
    ], string='Contract line Status', readonly=True, copy=False,  default='draft')
    
    won_uom_qty = fields.Float(string='Won Quantity', digits=dp.get_precision('Product Unit of Measure'))
    order_line = fields.One2many('sale.order.line', 'contract_line_id', string='Order Lines')

    invoicing = fields.Selection([
        ('to_invoice', 'Applicable'),
        ('do_not_invoice', 'Non applicable')
       ], string='Facturation',  default= 'to_invoice')
    
    pattern_not_invoicing = fields.Selection([
        ('starter_kit', 'Kit de démarrage'),
        ('mad', 'MAD'),
        ('warranty', 'Garantie'),
        ('loan_refund', 'Retour emprunt'),
        ('replacement', 'Remplacement'),
        ('commercial_gesture', 'Geste commercial'),
        ('promotional_offer', 'Offre promotionnelle'),
        ('std', 'Standard(s)'),
        ('accessory', 'Accessoire(s)') 
       ], string='Motif de facturation non applicable',  default= '')
    
    is_reactif_dedie = fields.Boolean(string='Réactif dédié')   
    is_reactif_manuel = fields.Boolean(string='Réactif manuel')  
    standard_ids = fields.Many2many('product.template', 'contract_line_reactif_standards_rel', 'reactif_id', 'standard_id',string='Standards',
        domain=[('is_standard', '=', True)])
    related_line_id = fields.Many2one('contract.lines', string='lines')
    tender_line_id = fields.Many2one('tender.line', string='lignes')

    @api.multi
    @api.depends('order_line','tender_id.order_ids','order_line.qty_delivered')
    def _compute_qty_delivered_all(self):
        for contract_line in self:
            qty = 0.0
            for order_line in contract_line.order_line : 
                qty += order_line.qty_delivered
            contract_line.qty_delivered = qty

    @api.multi
    def _get_display_price(self, product):
        if self.tender_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.tender_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.tender_id.partner_id.id, date=self.tender_id.begin_date, uom=self.product_uom.id)

        final_price, rule_id = self.tender_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.tender_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.tender_id.pricelist_id.id)
        if currency != self.tender_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.tender_id.pricelist_id.currency_id,
                self.tender_id.company_id, self.tender_id.begin_date or fields.Date.today())
        return max(base_price, final_price)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.tender_id.partner_id.lang,
            partner=self.tender_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.tender_id.begin_date,
            pricelist=self.tender_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        result = {'domain': domain}
        name = self.get_sale_order_line_multiline_description_sale(product)
        vals.update(name=name)
        self._compute_tax_id()
        if self.tender_id.pricelist_id and self.tender_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        if self.tender_id.contract_type == 'prived_mad' :
            if self.product_id.is_reactif_dedie :
                self.is_reactif_dedie =True
                self.standard_ids = [(6,0,self.product_id.standard_ids.ids)]
                self.is_reactif_manuel =False
            else :
                self.is_reactif_dedie =False    
                
            if self.product_id.is_reactif_manuel :
                self.is_reactif_manuel =True
                self.standard_ids = [(6,0,self.product_id.standard_ids.ids)]
                self.is_reactif_dedie =False
                
            else :
                self.is_reactif_manuel =False   
        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.tender_id.pricelist_id and self.tender_id.partner_id:
            product = self.product_id.with_context(
                lang=self.tender_id.partner_id.lang,
                partner=self.tender_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.tender_id.begin_date,
                pricelist=self.tender_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

    @api.multi
    def name_get(self):
        result = []
        for so_line in self.sudo():
            name = '%s - %s' % (so_line.tender_id.name, so_line.name.split('\n')[0] or so_line.product_id.name)
            if so_line.order_partner_id.ref:
                name = '%s (%s)' % (name, so_line.order_partner_id.ref)
            result.append((so_line.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = expression.AND([
                args or [],
                ['|', ('tender_id.name', operator, name), ('name', operator, name)]
            ])
        return super(ContractLines, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.tender_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or(product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.user.company_id, self.tender_id.date_order or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _get_protected_fields(self):
        return [
            'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty',
            'tax_id', 'analytic_tag_ids'
        ]

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.tender_id.partner_id and self.tender_id.pricelist_id and
                self.tender_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.tender_id.partner_id.lang,
            partner=self.tender_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.tender_id.date_order,
            pricelist=self.tender_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )
        product_context = dict(self.env.context, partner_id=self.tender_id.partner_id.id, date=self.tender_id.date_order, uom=self.product_uom.id)
        price, rule_id = self.tender_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.tender_id.partner_id)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.tender_id.pricelist_id.id)
        if new_list_price != 0:
            if self.tender_id.pricelist_id.currency_id != currency:
                new_list_price = currency._convert(
                    new_list_price, self.tender_id.pricelist_id.currency_id,
                    self.tender_id.company_id, self.tender_id.date_order or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if discount > 0:
                self.discount = discount

    def _is_delivery(self):
        self.ensure_one()
        return False

    def get_sale_order_line_multiline_description_sale(self, product):
        return product.get_product_multiline_description_sale() 

class ContractExtraLines(models.Model):
    _name = 'contract.extra.lines'
    _description = 'Contract Extra Line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.tender_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.tender_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            
            
    @api.depends('tender_id.order_ids','order_line','order_line.qty_invoiced','order_line.qty_to_invoice','order_line.invoice_lines')
    def _get_subtotal_values(self):
        for contract_line in self:
            amount_taxexcl_invoiced = 0.0
            amount_taxexcl_to_invoice = 0.0
            for order_line in contract_line.order_line : 
                amount_taxexcl_invoiced   += order_line.price_reduce_taxexcl * order_line.qty_invoiced
                amount_taxexcl_to_invoice += order_line.price_reduce_taxexcl * order_line.qty_to_invoice
            contract_line.subtotal_invoiced = amount_taxexcl_invoiced
            contract_line.subtotal_to_invoice = amount_taxexcl_to_invoice         
            contract_line.subtotal_encours = amount_taxexcl_invoiced + amount_taxexcl_to_invoice

    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.depends('price_total', 'product_uom_qty')
    def _get_price_reduce_tax(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_subtotal', 'product_uom_qty')
    def _get_price_reduce_notax(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.tender_id.partner_id.property_account_position_id
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.tender_id.partner_id) if fpos else taxes

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        return {}

    @api.model
    def _prepare_add_missing_fields(self, values):
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('tender_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values.update(self._prepare_add_missing_fields(values))
        lines = super().create(vals_list)
        return lines
    
    tender_id = fields.Many2one('tender.contract', string='Appel d\offre', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits=dp.get_precision('Product Price'), readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    qty_delivered = fields.Float('Delivered Quantity', digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    qty_invoiced = fields.Float(string='Invoiced Quantity', digits=dp.get_precision('Product Unit of Measure'))
    qty_to_invoice = fields.Float(string='To invoice Quantity', digits=dp.get_precision('Product Unit of Measure'))
    untaxed_amount_invoiced = fields.Float("Untaxed Invoiced Amount" , digits=dp.get_precision('Product Unit of Measure'))
    untaxed_amount_to_invoice = fields.Float("Untaxed Amount To Invoice" , digits=dp.get_precision('Product Unit of Measure'))
    subtotal_encours = fields.Float(string='Montant encours', readonly=True, digits=dp.get_precision('Product Unit of Measure'))
    salesman_id = fields.Many2one(related='tender_id.user_id', store=True, string='Salesperson', readonly=True)
    company_id = fields.Many2one(related='tender_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    order_partner_id = fields.Many2one(related='tender_id.partner_id', store=True, string='Customer', readonly=False)
    order_id = fields.Many2one('sale.order', string='Bon de commande', required=True, ondelete='cascade')
    
    @api.multi
    def _get_display_price(self, product):
        if self.tender_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.tender_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.tender_id.partner_id.id, date=self.tender_id.begin_date, uom=self.product_uom.id)

        final_price, rule_id = self.tender_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.tender_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.tender_id.pricelist_id.id)
        if currency != self.tender_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.tender_id.pricelist_id.currency_id,
                self.tender_id.company_id, self.tender_id.begin_date or fields.Date.today())
        return max(base_price, final_price)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.tender_id.partner_id.lang,
            partner=self.tender_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.tender_id.begin_date,
            pricelist=self.tender_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}
        name = self.get_sale_order_line_multiline_description_sale(product)
        vals.update(name=name)
        self._compute_tax_id()
        if self.tender_id.pricelist_id and self.tender_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.tender_id.pricelist_id and self.tender_id.partner_id:
            product = self.product_id.with_context(
                lang=self.tender_id.partner_id.lang,
                partner=self.tender_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.tender_id.date_order,
                pricelist=self.tender_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

    @api.multi
    def name_get(self):
        result = []
        for so_line in self.sudo():
            name = '%s - %s' % (so_line.tender_id.name, so_line.name.split('\n')[0] or so_line.product_id.name)
            if so_line.order_partner_id.ref:
                name = '%s (%s)' % (name, so_line.order_partner_id.ref)
            result.append((so_line.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = expression.AND([
                args or [],
                ['|', ('tender_id.name', operator, name), ('name', operator, name)]
            ])
        return super(ContractLines, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def get_sale_order_line_multiline_description_sale(self, product):
        return product.get_product_multiline_description_sale() 
