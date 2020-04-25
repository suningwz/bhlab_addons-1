# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

from odoo import fields, models, api
import calendar


class AccountExercice(models.Model):
    _name = 'account.exercice'
    _description = 'Exercice comptable'

    @api.one
    @api.depends('name')
    def _date_exercice(self):
        for rec in self:
            if rec.name:
                if len(rec.name) == 4 and rec.name.isdigit():
                    rec.date_debut = rec.name + '-01-01'
                    rec.date_fin = rec.name + '-12-31'

    name = fields.Char('Exercice', size=4, readonly=1, states={'draft': [('readonly', False)]})
    date_debut = fields.Date(compute=_date_exercice, string=u'Date début')
    date_fin = fields.Date(compute=_date_exercice, string='Date fin')
    period_ids = fields.One2many('account.exercice.period', 'exercice_id', string='Periodes', readonly=1)
    state = fields.Selection([('draft', 'Nouveau'), ('actif', 'Actif'), ('done', u'Cloturé')], string='Etat', default='draft')
    defaut = fields.Boolean('Exercice par défaut', readonly=True)

    @api.one
    def action_set_default(self):
        exes = self.env['account.exercice'].search([])
        for rec in exes:
            rec.defaut = False
        self.defaut = True

    @api.one
    def action_create_periodes(self):
        self.period_ids.unlink()
        for i in range(1, 13):
            mois = "{0:0>2}".format(str(i))
            self.env['account.exercice.period'].create({
                'name' : mois + '/' + self.name,
                'mois' : mois,
                'exercice_id': self.id,
            })
        self.state = 'actif'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Cet exercice existe deja !"),
    ]


class AccountExercicePeriod(models.Model):
    _name = 'account.exercice.period'
    _description = 'Periode comptable'

    @api.one
    @api.depends('mois', 'exercice_id')
    def _date_periode(self):
        for rec in self:
            if rec.exercice_id:
                rec.date_debut = rec.exercice_id.name + '-' + rec.mois + '-01'
                rec.date_fin = rec.exercice_id.name + '-' + rec.mois + '-' + str(calendar.monthrange(int(rec.exercice_id.name), int(rec.mois))[1])

    name = fields.Char('Exercice')
    mois = fields.Selection([('01', 'Jan'),
                             ('02', 'Fev'),
                             ('03', 'Mar'),
                             ('04', 'Avr'),
                             ('05', 'Mai'),
                             ('06', 'Jun'),
                             ('07', 'Jui'),
                             ('08', 'Aout'),
                             ('09', 'Sep'),
                             ('10', 'Oct'),
                             ('11', 'Nov'),
                             ('12', 'Dec'),
                             ], string='Mois')

    exercice_id = fields.Many2one('account.exercice', string='Exercice')
    date_debut = fields.Date(compute=_date_periode, string=u'Date début')
    date_fin = fields.Date(compute=_date_periode, string='Date fin')

