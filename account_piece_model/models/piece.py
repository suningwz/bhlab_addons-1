# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _name    = "account.move"
    _inherit = "account.move"

    @api.multi
    def action_saisie_assistee(self):
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('account_piece_model', 'saisie_assistee_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Saisie assistee',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'account.saisie.assistee.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_move_id': self.id, 'default_journal_id': self.journal_id.id},
            'target': 'new',
        }
