# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountReportReportBalance(models.Model):
    _name    = 'dl.report.balance'
    _description = 'Balance des comptes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order   = 'name'

    @api.model
    def _get_default_exercice(self):
        exe = self.env['account.exercice'].search([('defaut', '=', True)])
        if exe.exists():
            return exe[0].id
        else:
            return None

    @api.model
    def _get_default_unit(self):
        unit = self.env['account.report.unite'].search([('division', '=', 1)])
        if unit.exists():
            return unit.id
        else:
            return None

    @api.one
    @api.depends('line_ids')
    def _totaux(self):
        for rec in self:
            rec.init_debit     = sum(line.init_debit for line in rec.line_ids)
            rec.inti_credit    = sum(line.inti_credit for line in rec.line_ids)
            rec.periode_debit  = sum(line.periode_debit for line in rec.line_ids)
            rec.periode_credit = sum(line.periode_credit for line in rec.line_ids)
            rec.solde_debit    = sum(line.solde_debit for line in rec.line_ids)
            rec.solde_credit   = sum(line.solde_debit for line in rec.line_ids)

    name        = fields.Char('Titre', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    code        = fields.Char('Code', required=True, readonly=1, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise')

    date_debut  = fields.Date(u'Date début', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    date_fin    = fields.Date('Date fin', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    exercice_id = fields.Many2one('account.exercice', string='Exercice', required=True, default=_get_default_exercice, readonly=1, states={'draft': [('readonly', False)]})
    exercice    = fields.Char(related='exercice_id.name', size=4, readonly=True)
    devise_id   = fields.Many2one('account.report.unite', string=u'Unité d\'affichage', default=_get_default_unit, required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')

    line_ids    = fields.One2many('dl.report.balance.line', 'report_id', copy=True, string='Lignes', readonly=1)
    state       = fields.Selection([('draft', 'Brouillon'), ('done', u'Terminé')], string='Etat', default='draft', track_visibility='onchange')
    parent_id   = fields.Many2one('dl.report.balance', string='Balance N-1', readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')

    notes       = fields.Text('Notes')

    init_debit     = fields.Monetary(compute=_totaux, string=u'Débit initial')
    inti_credit    = fields.Monetary(compute=_totaux, string=u'Crédit initial')
    periode_debit  = fields.Monetary(compute=_totaux, string=u'Débit période')
    periode_credit = fields.Monetary(compute=_totaux, string=u'Crédit période')
    solde_debit    = fields.Monetary(compute=_totaux, string=u'Solde débit')
    solde_credit   = fields.Monetary(compute=_totaux, string=u'Solde crédit')

    @api.onchange('exercice_id')
    def onchange_date(self):
        if self.exercice_id:
            # if not self.date_debut:
            self.date_debut = self.exercice_id.name+'-01-01'
            # if not self.date_fin:
            self.date_fin = self.exercice_id.name + '-12-31'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def total_compte(self):
        self.line_ids.unlink()

        # ajout des comptes
        req_cpt  = "select distinct account_move_line.account_id, account_account.code as code " \
                   "from account_move_line, account_account, account_move " \
                   "where account_move.date between %s and %s " \
                   "and account_account.id = account_move_line.account_id " \
                   "and account_move.id = account_move_line.move_id "
                   # "and journal_id not in (21,23) order by code"
        print(self.date_debut)
        rub = (self.date_debut, self.date_fin,)
        self._cr.execute(req_cpt, rub)
        res_cpt = self._cr.dictfetchall()
        if res_cpt:
            for rec in res_cpt:
                # calcul des montants
                # debit et credit initial
                req_1 = "select sum(credit) as credit, sum(debit) as debit " \
                        "from account_move_line, account_account, account_move, account_journal " \
                        "where account_move.date between %s and %s and account_account.code = %s " \
                        "and account_account.id = account_move_line.account_id " \
                        "and account_move.id = account_move_line.move_id " \
                        "and account_move.journal_id = account_journal.id " \
                        "and account_journal.saisie = 'automatic'"

                rub = (self.date_debut, self.date_fin, rec.get('code'), )
                self._cr.execute(req_1, rub)
                res_1 = self._cr.dictfetchall()
                credit_initial = 0.0
                debit_initial = 0.0
                if res_1:
                    if res_1[0].get('credit'):
                        credit_initial = res_1[0].get('credit')
                    if res_1[0].get('debit'):
                        debit_initial = res_1[0].get('debit')
                # calcul solde
                if credit_initial != 0 and debit_initial != 0:
                    if credit_initial > debit_initial:
                        credit_initial = credit_initial - debit_initial
                        debit_initial = 0
                    elif debit_initial > credit_initial:
                        debit_initial = debit_initial - credit_initial
                        credit_initial = 0

                # debit et credit periode
                req_2 = "select sum(credit) as credit, sum(debit) as debit " \
                        "from account_move_line, account_account, account_move, account_journal  " \
                        "where account_move.date between %s and %s and account_account.code = %s " \
                        "and account_account.id = account_move_line.account_id " \
                        "and account_move.id = account_move_line.move_id " \
                        "and account_move.journal_id = account_journal.id " \
                        "and account_journal.saisie = 'manual'"

                rub = (self.date_debut, self.date_fin, rec.get('code'), )
                self._cr.execute(req_2, rub)
                res_2 = self._cr.dictfetchall()
                credit_periode = 0.0
                debit_periode = 0.0
                if res_2:
                    if res_2[0].get('credit'):
                        credit_periode = res_2[0].get('credit')
                    if res_2[0].get('debit'):
                        debit_periode = res_2[0].get('debit')

                solde_credit = credit_periode + credit_initial
                solde_debit = debit_periode + debit_initial
                if solde_debit>solde_credit:
                    solde_debit = solde_debit - solde_credit
                    solde_credit = 0.0
                else:
                    solde_credit = solde_credit - solde_debit
                    solde_debit = 0.0

                self.env['dl.report.balance.line'].create({
                    'name': rec.get('account_id'),
                    'code': rec.get('code'),
                    'report_id': self.id,
                    'init_debit': debit_initial,
                    'inti_credit': credit_initial,
                    'periode_debit': debit_periode,
                    'periode_credit': credit_periode,
                    'solde_debit': solde_debit,
                    'solde_credit': solde_credit,
                })

    @api.one
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le rapport est validé ! \n\n Remettez en brouillon pour pouvoir supprimer'))
        else:
            self.line_ids.unlink()
            rec = super(AccountReportReportBalance, self).unlink()
            return rec

    @api.multi
    def copy(self, default=None):
        default = default or {}

        default['name'] = self.name + ' (Copie)'
        return super(AccountReportReportBalance, self).copy(default)


class AccountReportBalanceLine(models.Model):
    _name        = 'dl.report.balance.line'
    _order       = 'code'

    name           = fields.Many2one('account.account', required=True)
    code           = fields.Char('Code')
    compte         = fields.Char(related='name.name', string=u'Intitulé')
    report_id      = fields.Many2one('dl.report.balance', string='Balance')
    currency_id    = fields.Many2one(related='report_id.devise_id', string='Devise')
    init_debit     = fields.Float(u'Débit initial')
    inti_credit    = fields.Float(u'Crédit initial')
    periode_debit  = fields.Float(u'Débit période')
    periode_credit = fields.Float(u'Crédit période')
    solde_debit    = fields.Float(u'Solde débit')
    solde_credit   = fields.Float(u'Solde crédit')
