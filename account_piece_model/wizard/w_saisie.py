# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaisieAssistee(models.TransientModel):
    _name = 'account.saisie.assistee.wizard'

    move_id  = fields.Many2one('account.move', required=True, readonly="1")
    journal_id  = fields.Many2one('account.journal', required=True)
    modele_id   = fields.Many2one('account.piece.modele', required=True)
    montant     = fields.Monetary('Montant total')
    currency_id = fields.Many2one(related='journal_id.currency_id')
    line_ids    = fields.One2many('account.saisie.assistee.line.wizard', 'wizard_id', string='Ecritures')

    @api.onchange('modele_id')
    def onchange_modele(self):
        if self.modele_id:
            self.line_ids.unlink()
            line = []
            for rec in self.modele_id.line_ids:
                if rec.debit_credit == 'Debit':
                    debit = self.montant * rec.taux / 100.0
                    credit = 0.0
                else:
                    debit = 0.0
                    credit = self.montant * rec.taux / 100.0

                line.append({
                    'account_id' : rec.account_id.id,
                    'libelle'    : rec.libelle,
                    'debit'      : debit,
                    'credit'     : credit,
                    'wizard_id'  : self.id,
                })

            self.line_ids = line

    @api.multi
    def action_validate(self):
        line = []
        for rec in self.line_ids:
            line.append({
                'account_id': rec.account_id.id,
                'name': rec.libelle,
                'debit': rec.debit,
                'credit': rec.credit,
                'move_id': self.move_id.id,
            })

        self.move_id.ref = self.modele_id.reference
        self.move_id.journal_id = self.modele_id.journal_id.id
        self.move_id.quantity = 1.0
        self.move_id.line_ids.unlink()
        self.move_id.line_ids = line


class SaisieAssisteeLine(models.TransientModel):
    _name = 'account.saisie.assistee.line.wizard'

    account_id  = fields.Many2one('account.account')
    libelle     = fields.Char('Designation')
    debit       = fields.Monetary(u'Débit')
    credit      = fields.Monetary(u'Crédit')
    currency_id = fields.Many2one(related='wizard_id.currency_id')
    wizard_id   = fields.Many2one('account.saisie.assistee.wizard', string='Wizard')
