# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class ReportAccountHt(models.Model):
    _name = 'report.account.ht'

    name = fields.Char('Compte')


class ReportAccountTva(models.Model):
    _name = 'report.account.tva'

    name = fields.Char('Compte')


class AccountEtatTva(models.Model):
    _name = 'account.etat.tva'
    _description = 'Etat TVA a recuperer'
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
            rec.total_ht = sum(line.total_ht for line in rec.line_ids)
            rec.total_tva = sum(line.total_tva for line in rec.line_ids)
            rec.total_ttc = rec.total_ht + rec.total_tva

    name       = fields.Char('Numero', readonly=True)
    exercice_id = fields.Many2one('account.exercice', string='Exercice', required=True, default=_get_default_exercice, readonly=1, states={'draft': [('readonly', False)]})
    period_id  = fields.Many2one('account.exercice.period', string='Periode', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_debut = fields.Date(related='period_id.date_debut', string='Date debut', store=True)
    date_fin   = fields.Date(related='period_id.date_fin', string='Date fin')
    line_ids   = fields.One2many('account.etat.tva.line', 'etat_tva_id', string='Ligne', readonly=1, states={'draft': [('readonly', False)]})
    type       = fields.Selection([('Achat', 'Achats et services'), ('Invest', 'Investissement')], string='Type', default='Achat', readonly=1, states={'draft': [('readonly', False)]})
    type_calcul = fields.Selection([('Facture', 'Facture'), ('Ecriture', 'Ecritures')], string='Type de calcul', default='Facture', readonly=1, states={'draft': [('readonly', False)]})
    total_ht   = fields.Monetary(compute=_totaux, string='Total HT')
    total_tva  = fields.Monetary(compute=_totaux, string='Total TVA')
    total_ttc  = fields.Monetary(compute=_totaux, string='Total TTC')
    company_id = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', readonly=1)

    journal_ch  = fields.Char('Journaux')
    ht_inv_tva  = fields.Char('Comptes HT (investissements)')
    tva_inv_tva = fields.Char('Comptes TVA (investissements)')

    ht_ach_tva  = fields.Char('Comptes HT (Achats et services)')
    tva_ach_tva = fields.Char('Comptes TVA (Achats et services)')

    state = fields.Selection([('draft', 'Nouveau'), ('done', u'Terminé')], string='Etat', default='draft')

    def compute_account(self, list_account, list_journal, field_mtn):
        for cpt in list_account.split(","):
            req = "select sum(debit) as d, sum(credit) as c, account_account.code as cpt, account_move.date, account_move.id as piece, account_move_line.partner_id, account_move.journal_id "\
                  "from account_move_line, account_move, account_account "\
                  "where account_move.date between %s and %s "\
                  "and account_account.code like %s "\
                  "and account_account.id = account_id and account_move.id = account_move_line.move_id "

            if list_journal:
                req += 'and account_move.journal_id in (' + list_journal + ') '
            req += 'group by account_move.date, account_move.id, account_move_line.partner_id, account_move.journal_id, account_account.code order by date;'

            self._cr.execute(req, (self.date_debut, self.date_fin, cpt + '%'))
            res = self._cr.dictfetchall()
            i = 0

            for rec in res:
                i += 1
                line = self.env['account.etat.tva.line'].search([('piece_id', '=', rec.get('piece')), ('etat_tva_id', '=', self.id)])
                if not line.exists():
                    self.env['account.etat.tva.line'].create({
                        'name'      : i,
                        'invoice_id': None,
                        'partner_id': rec.get('partner_id'),
                        field_mtn  : rec.get('d') - rec.get('c'),
                        # 'total_tva' : 0.0,
                        'piece_id'  : rec.get('piece'),
                        'account'   : rec.get('cpt'),
                        'etat_tva_id' : self.id,
                        'date'      : rec.get('date'),
                    })
                else:
                    if field_mtn == 'total_ht':
                        line.total_ht += rec.get('d') - rec.get('c')
                    else:
                        line.total_tva += rec.get('d') - rec.get('c')
                    line.account += ', ' + rec.get('cpt')

    @api.one
    def compute_data(self):
        def get_journaux():
            if self.journal_ch:
                lstj = self.journal_ch.split(",")
                list_j = ''
                for jrn in lstj:
                    journal = self.env['account.journal'].search([('code', '=', jrn)])
                    if journal.exists():
                        list_j += str(journal.id) + ','
                return list_j[:-1]
            else:
                return ''
        if self.type == 'Achat':
            ht_cpt  = self.ht_ach_tva
            tva_cpt = self.tva_ach_tva
        else:
            ht_cpt  = self.ht_inv_tva
            tva_cpt = self.tva_inv_tva

        if self.type_calcul == 'Ecriture':
            if ht_cpt and tva_cpt:
                self.line_ids.unlink()
                self.compute_account(ht_cpt, get_journaux(), 'total_ht')
                self.compute_account(tva_cpt, get_journaux(), 'total_tva')
            else:
                raise UserError(_(
                    u'Calcul annulé ! \n\n  Veuiller d\'abord rentrer les paramétres (Jounaux, comptes HT et comptes TVA)'))
        else:
            self.line_ids.unlink()
            fact = self.env['account.invoice'].search([('type', '=', 'in_invoice'),
                                                       ('state', '!=', 'draft'),
                                                       ('date_invoice', '>', self.date_debut),
                                                       ('date_invoice', '<', self.date_fin),
                                                       ])
            i = 0
            for rec in fact:
                for ligne in rec.invoice_line_ids:
                    if self.type == 'Achat' and not ligne.asset_category_id:
                        fc_ligne = self.env['account.etat.tva.line'].search([('invoice_id', '=', rec.id), ('etat_tva_id', '=', self.id)])
                        if fc_ligne.exists():
                            fc_ligne.total_ht  += ligne.price_subtotal
                            fc_ligne.total_tva += ligne.price_total - ligne.price_subtotal
                        else:
                            i += 1
                            self.env['account.etat.tva.line'].create({
                                'name': i,
                                'invoice_id': rec.id,
                                'partner_id': rec.partner_id.id,
                                'total_ht'  : ligne.price_subtotal,
                                'total_tva' : ligne.price_total - ligne.price_subtotal,
                                'piece_id'  : rec.move_id.id,
                                'account'   : ligne.account_id.code,
                                'numero': rec.number,
                                'etat_tva_id': self.id,
                                'date': rec.date_invoice,
                            })
                    else:
                        if self.type == 'Invest' and ligne.asset_category_id:
                            fc_ligne = self.env['account.etat.tva.line'].search([('invoice_id', '=', rec.id), ('etat_tva_id', '=', self.id)])
                            if fc_ligne.exists():
                                fc_ligne.total_ht += ligne.price_subtotal
                                fc_ligne.total_tva += ligne.price_total - ligne.price_subtotal
                            else:
                                i += 1
                                self.env['account.etat.tva.line'].create({
                                    'name': i,
                                    'invoice_id': rec.id,
                                    'partner_id': rec.partner_id.id,
                                    'total_ht': ligne.price_subtotal,
                                    'total_tva': ligne.price_total - ligne.price_subtotal,
                                    'piece_id': rec.move_id.id,
                                    'account': ligne.account_id.code,
                                    'numero' : rec.number,
                                    'etat_tva_id': self.id,
                                    'date': rec.date_invoice,
                                })

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('account.etat.tva') or '/'
        return super(models.Model, self).create(vals)

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
            return super(AccountEtatTva, self).unlink()


class AccountEtatTvaLine(models.Model):
    _name = 'account.etat.tva.line'
    _description = 'Etat TVA Line'

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
    invoice_id           = fields.Many2one('account.invoice', string='Facture')
    date                 = fields.Date('Date facture')
    numero               = fields.Char(u'Numéro facture')
    partner_id           = fields.Many2one('res.partner', string='Tiers')
    partner_adress       = fields.Char(compute=_get_address, string='Adresse', readonly=True)
    partner_num_agrement = fields.Char(related='partner_id.num_agrement', string=u'N° CA/Agrément', readonly=True)
    partner_rc           = fields.Char(related='partner_id.rc', string='RC', readonly=True)
    partner_nif          = fields.Char(related='partner_id.nif', string='N° IDF', readonly=True)
    partner_ai           = fields.Char(related='partner_id.ai', string='ART', readonly=True)
    total_ht             = fields.Float('Total HT')
    total_tva            = fields.Float('Total TVA')
    total_ttc            = fields.Float('Total TTC')
    piece_id             = fields.Many2one('account.move')
    account              = fields.Char('Compte')
    etat_tva_id          = fields.Many2one('account.etat.tva')

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            self.numero = self.invoice_id.number
            self.date   = self.invoice_id.date
