# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class AccountReportGroup(models.Model):
    _name    = 'account.report.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Groupe', required=True)
    code       = fields.Char('Code')
    notes      = fields.Text('Notes')
    report_ids = fields.One2many('dl.account.report.report', 'groupe_id', string='Rapports')
    model_ids = fields.One2many('account.report.model', 'groupe_id', string='Models de rapports')

    def open_wizard(self):
        return {
            'name': _('Création des rapports'),
            'view_mode': 'form',
            'res_model': 'grp.create.report.wizard',
            'view_id': self.env.ref('l10n_dz_reports.group_create_report_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_name': self.id,
            },
            'target': 'new',
        }


class AccountReportUnite(models.Model):
    _name = 'account.report.unite'

    name = fields.Char(u'Unité d\'affichage')
    division = fields.Integer('Diviser le montant par ')


class Periode(models.Model):
    _name = 'periode'

    name        = fields.Char('Periode', required=True)
    exercice    = fields.Char('Exercice', saize=4, required=True)
    date_from   = fields.Date(u'Date début', required=True)
    date_to     = fields.Date('Date fin', required=True)
    periode_sel = fields.Selection([('Exercice', 'Exercice'), ('1er Trimestre', '1er Trimestre'),
                                    ('2eme Trimestre', '2eme Trimestre'), ('3eme Trimestre', '3eme Trimestre'),
                                    ('4eme Trimestre', '4eme Trimestre'), ], 'Liste periodes')

    @api.onchange('periode_sel', 'exercice')
    def on_change_selection(self):
        if self.periode_sel and self.exercice:
            self.name = self.periode_sel + ' ' + self.exercice

            per = self.periode_sel
            # maj des dates
            if per[:8] == 'Exercice':
                self.date_from = self.exercice + '-01-01'
                self.date_to = self.exercice + '-12-31'
            else:
                if per[:1] == '1':
                    self.date_from = self.exercice + '-01-01'
                    self.date_to = self.exercice + '-03-31'
                else:
                    if per[:1] == '2':
                        self.date_from = self.exercice + '-01-01'
                        self.date_to = self.exercice + '-06-30'
                    else:
                        if per[:1] == '3':
                            self.date_from = self.exercice + '-01-01'
                            self.date_to = self.exercice + '-09-30'
                        else:
                            self.date_from = self.exercice + '-01-01'
                            self.date_to = self.exercice + '-12-31'

    @api.constrains('exercice')
    def _check_exercice(self):
        exe_max = datetime.now().year + 1
        if self.exercice < '1980' or self.exercice > str(exe_max):
            raise Warning('Veuillez verifier la valeur de l\'exercice saisi')
