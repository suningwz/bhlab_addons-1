# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class AccountEtatTap(models.Model):
    _name = 'account.etat.tap'
    _description = 'Etat taxe sur chiffre affaire a payer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_exercice(self):
        exe = self.env['account.exercice'].search([('defaut', '=', True)])
        if exe.exists():
            return exe[0].id
        else:
            return None

    @api.one
    @api.depends('line_ids')
    def _totaux(self):
        for rec in self:
            rec.total_ht  = sum(line.total_ht for line in rec.line_ids)
            rec.total_tva = sum(line.total_tva for line in rec.line_ids)
            rec.total_tap = sum(line.total_tap for line in rec.line_ids)
            rec.total_ttc = rec.total_ht + rec.total_tva

    name        = fields.Char('Numero', readonly=True)
    exercice_id = fields.Many2one('account.exercice', string='Exercice', required=True, default=_get_default_exercice, readonly=1, states={'draft': [('readonly', False)]})
    period_id   = fields.Many2one('account.exercice.period', string='Periode', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_debut  = fields.Date(related='period_id.date_debut', string='Date debut', store=True)
    date_fin    = fields.Date(related='period_id.date_fin', string='Date fin')
    line_ids    = fields.One2many('account.etat.tap.line', 'etat_tap_id', string='Ligne', readonly=1, states={'draft': [('readonly', False)]})
    total_ht    = fields.Monetary(compute=_totaux, string='Total HT')
    total_tva   = fields.Monetary(compute=_totaux, string='Total TVA')
    total_ttc   = fields.Monetary(compute=_totaux, string='Total TTC')
    total_tap   = fields.Monetary(compute=_totaux, string='Total TAP')
    type_calcul = fields.Selection([('Facture', 'Facture'), ('Ecriture', 'Ecritures')], string='Type de calcul', default='Facture', readonly=1, states={'draft': [('readonly', False)]})
    company_id  = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', readonly=1)
    journal_104 = fields.Char('Journaux')
    ht_104      = fields.Char('Comptes HT')
    tva_104     = fields.Char('Comptes TVA')
    tap_tap     = fields.Char('Comptes TAP')
    state       = fields.Selection([('draft', 'Nouveau'), ('done', u'Terminé')], string='Etat', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('account.etat.tap') or '/'
        return super(models.Model, self).create(vals)

    @api.one
    def compute_data(self):
        if True:
            self.line_ids.unlink()
            fact = self.env['account.invoice'].search([('type', '=', 'out_invoice'),
                                                       ('state', '!=', 'draft'),
                                                       ('date_invoice', '>', self.date_debut),
                                                       ('date_invoice', '<', self.date_fin),
                                                       ])
            i = 0
            for rec in fact:
                i += 1
                self.env['account.etat.tap.line'].create({
                    'name'      : i,
                    'invoice_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'date'      : rec.date_invoice,
                    'total_ht'  : rec.amount_untaxed_signed,
                    'total_tva' : rec.amount_tax,
                    'numero'    : rec.number,
                    'etat_tap_id': self.id,
                })

    @api.one
    def action_validate(self):
        if self.date_fin < str(date.today()):
            self.state = 'done'
        else:
            raise UserError(_(u'La date de fin du document n\'a pas encore été atteinte ! \n\n  Le document ne peut etre cloturé !'))

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le document est déjà validé !'))
        else:
            self.line_ids.unlink()
            return super(AccountEtatTap, self).unlink()


class AccountEtatTapLine(models.Model):
    _name = 'account.etat.tap.line'
    _description = 'Etat TAP Line'

    @api.one
    @api.depends('total_ht', 'total_tva')
    def _totaux(self):
        for rec in self:
            rec.total_ttc = rec.total_ht + rec.total_tva
            rec.total_tap = rec.total_ht * 0.02

    name        = fields.Integer('Numero')
    invoice_id  = fields.Many2one('account.invoice', string='Facture')
    date        = fields.Date(related='invoice_id.date', string='Date facture')
    partner_id  = fields.Many2one('res.partner', string='Tiers')
    total_ht    = fields.Float(string='Total HT')
    total_tva   = fields.Float(string='Total TVA')
    total_ttc   = fields.Float(compute=_totaux, string='Total TTC')
    total_tap   = fields.Float(compute=_totaux, string='Total TAP')
    etat_tap_id = fields.Many2one('account.etat.tap')
