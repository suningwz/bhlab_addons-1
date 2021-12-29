from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('account_review', 'Approve For Sale Order'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        readonly=True, copy=False, index=True, tracking=3, default='draft')
    in_approve = fields.Boolean('In Approve')

    def action_confirm(self):
        partner = self.partner_id

        if partner.credit_limit > 0:
            if partner.credit > partner.credit_limit:
                view_id = self.env.ref(
                    'customer_credit_management.credit_management_limit_wizard').id
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.customer.credit.limit.wizard',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'name': 'Customer Credit Limit',
                    'views': [[view_id, 'form']],
                    'context': {'current_id': self.id}
                }
            else:
                credit = 0
                total_sales = 0
                sale_amt = 0
                inv_total_amt = 0
                inv_total_amt_draft = 0
                inv_rec = self.env['account.invoice'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'not in', ['draft', 'cancel'])])
                inv_rec_draft = self.env['account.invoice'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'not in', ['cancel'])])
                sale_amount = self.search(
                    [('partner_id', '=', partner.id),
                     ('invoice_status', '=', 'to invoice'),
                     ]).mapped('amount_total')
                sale_amount_current = self.search(
                    [('partner_id', '=', partner.id),
                     ('name', '=', self.name),
                     ]).mapped('amount_total')

                sale_amt = sum([sale for sale in sale_amount])
                sale_amt_current = sum([sale for sale in sale_amount_current])
                for inv in inv_rec:
                    inv_total_amt += inv.amount_total - inv.residual
                for inv in inv_rec_draft:
                    inv_total_amt_draft += inv.amount_total

                total_sales = inv_total_amt_draft - inv_total_amt + sale_amt + sale_amt_current
                if total_sales > partner.credit_limit:
                    view_id = self.env.ref(
                        'customer_credit_management.credit_management_limit_wizard').id
                    return {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'sale.customer.credit.limit.wizard',
                        'target': 'new',
                        'type': 'ir.actions.act_window',
                        'name': 'Customer Credit Limit',
                        'views': [[view_id, 'form']],
                        'context': {'current_id': self.id}
                    }
                else:
                    super(SaleOrder, self).action_confirm()
        else:
            super(SaleOrder, self).action_confirm()

    def action_account_approve(self):
        if self.env.user.has_group('customer_credit_management.group_allow_confirm_SO_over_limits'):
            super(SaleOrder, self).action_confirm()
        else:
            raise UserError((
                " Please contact your Administrator For SALE ORDER approval"))
