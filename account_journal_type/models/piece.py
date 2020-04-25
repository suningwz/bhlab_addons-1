# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _name    = "account.move"
    _inherit = "account.move"

    @api.multi
    def _get_default_journal_2(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id), ('saisie', '=', 'manual'), ('type', '=', self.env.context['default_journal_type'])], limit=1).id

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'posted': [('readonly', True)]}, default=_get_default_journal_2)
