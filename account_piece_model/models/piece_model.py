# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPieceModele(models.Model):
    _name    = "account.piece.modele"
    _description = "Modele de piece comptable"

    name       = fields.Char('Designation', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    reference  = fields.Char(u'Référence')
    line_ids   = fields.One2many('account.piece.modele.line', 'model_id', string='Lignes')

    @api.multi
    def action_create_move(self):
        move = self.env['account.move'].create({
            'ref': self.reference,
            'journal_id': self.journal_id.id,
            'quantity': 1,
        })
        line = []
        for rec in self.line_ids:
            line.append({
                'account_id': rec.account_id.id,
                'name': rec.libelle,
                'debit': 0.0,
                'credit': 0.0,
                'move_id': move.id,
            })
        move.line_ids = line

        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('account', 'view_move_form')
        form_view_id = move.id
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
                'name': 'Piece comptable',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'views': [(form_view_id, 'form'), ],
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'res_id' : move.id,
                # 'context': {'default_name': self.id},
                'target': 'new',
        }


class AccountPieceModeleLine(models.Model):
    _name = "account.piece.modele.line"
    _description = "Ligne du modele de piece comptable"

    account_id = fields.Many2one('account.account', string='Compte', required=True)
    libelle = fields.Char(u'Référence')
    debit_credit = fields.Selection([('Debit', u'Débit'), ('Credit', u'Crédit')], string='Le sense', required=True)
    taux = fields.Integer('Taux montant (%)')
    model_id = fields.Many2one('account.piece.modele', string=u'Modèle')
