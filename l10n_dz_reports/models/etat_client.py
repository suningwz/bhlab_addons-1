# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class AccountEtatClient(models.Model):
    _name = 'account.etat.client'
    _description = 'Etat client'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.one
    @api.depends('line_ids')
    def _totaux(self):
        for rec in self:
            rec.total_ht = sum(line.total_ht for line in rec.line_ids)
            rec.total_tva = sum(line.total_tva for line in rec.line_ids)
            rec.total_ttc = rec.total_ht + rec.total_tva

    @api.model
    def _get_default_exercice(self):
        exe = self.env['account.exercice'].search([('defaut', '=', True)])
        if exe.exists():
            return exe[0].id
        else:
            return None

    name        = fields.Char('Numero', readonly=True)
    exercice_id = fields.Many2one('account.exercice', string='Exercice', required=True, default=_get_default_exercice, readonly=1, states={'draft': [('readonly', False)]})
    period_id   = fields.Many2one('account.exercice.period', string='Periode', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_debut  = fields.Date(related='period_id.date_debut', string='Date debut', store=True)
    date_fin    = fields.Date(related='period_id.date_fin', string='Date fin')
    line_ids    = fields.One2many('account.etat.client.line', 'etat_client_id', string='Lignes', readonly=1, states={'draft': [('readonly', False)]})
    total_ht    = fields.Float(compute=_totaux, string='Total HT')
    total_tva   = fields.Float(compute=_totaux, string='Total TVA')
    total_ttc   = fields.Float(compute=_totaux, string='Total TTC')
    type_calcul = fields.Selection([('Facture', 'Facture'), ('Ecriture', 'Ecritures')], string='Type de calcul', default='Facture', readonly=1, states={'draft': [('readonly', False)]})
    company_id  = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', readonly=1)

    journal_104 = fields.Char('Journaux')
    ht_104      = fields.Char('Comptes HT')
    tva_104     = fields.Char('Comptes TVA')
    state = fields.Selection([('draft', 'Nouveau'), ('done', u'Terminé')], string='Etat', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('account.etat.client') or '/'
        return super(models.Model, self).create(vals)

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
                ligne = self.env['account.etat.client.line'].search([('partner_id', '=', rec.partner_id.id), ('etat_client_id', '=', self.id)])
                if ligne.exists():
                    ligne.total_ht += rec.amount_untaxed_signed
                    ligne.total_tva += rec.amount_tax
                    ligne.total_ttc += rec.amount_untaxed_signed + rec.amount_tax
                else:
                    i += 1
                    self.env['account.etat.client.line'].create({
                        'name'      : i,
                        'partner_id': rec.partner_id.id,
                        'total_ht'  : rec.amount_untaxed_signed,
                        'total_tva' : rec.amount_tax,
                        'total_ttc' : rec.amount_untaxed_signed + -rec.amount_tax,
                        'etat_client_id': self.id,
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
            return super(AccountEtatClient, self).unlink()


class AccountEtatClientLine(models.Model):
    _name = 'account.etat.client.line'
    _description = 'Etat Client Line'

    @api.one
    @api.depends('partner_id')
    def _get_address(self):
        adr = ''
        if self.partner_id:
            if self.partner_id.street:
                adr += self.partner_id.street + ', '
            if self.partner_id.street2:
                adr += self.partner_id.street2 + ', '
            if self.partner_id.city:
                adr += self.partner_id.city + ', '
            if self.partner_id.state_id:
                adr += self.partner_id.state_id.name + ', '
            if self.partner_id.zip:
                adr += 'CP ' + self.partner_id.zip + ', '
            if self.partner_id.country_id:
                adr += self.partner_id.country_id.name + '.'
        self.partner_adress = adr

    name                 = fields.Integer('Numero')
    partner_id           = fields.Many2one('res.partner', string='Client')
    partner_adress       = fields.Char(compute=_get_address, string='Adresse', readonly=True)
    partner_num_agrement = fields.Char(related='partner_id.num_agrement', string=u'N° CA/Agrément', readonly=True)
    partner_rc           = fields.Char(related='partner_id.rc', string='RC', readonly=True)
    partner_nif          = fields.Char(related='partner_id.nif', string='N° IDF', readonly=True)
    partner_ai           = fields.Char(related='partner_id.ai', string='ART', readonly=True)
    total_ht             = fields.Float(string='Total HT')
    total_tva            = fields.Float(string='Total TVA')
    total_ttc            = fields.Float(string='Total TTC')
    etat_client_id       = fields.Many2one('account.etat.client')
