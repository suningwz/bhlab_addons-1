# -*- coding: utf-8 -*-
from odoo import models, fields


class GrpCreateReportWizard(models.TransientModel):
    _name = 'grp.create.report.wizard'

    name        = fields.Many2one('account.report.group', required=1, readonly=1)
    balance_id  = fields.Many2one('dl.report.balance', string='Balance', required=True)
    date_debut  = fields.Date(related='balance_id.date_debut', string=u'Date début', readonly=1)
    date_fin    = fields.Date(related='balance_id.date_fin', string=u'Date fin', readonly=1)
    exercice    = fields.Char(related='balance_id.exercice', string='Exercice', readonly=1)
    devise_id   = fields.Many2one(related='balance_id.devise_id', string=u'Unité d\'affichage', readonly=1)
    valid       = fields.Boolean('Créer les rapports juste pour les modèles validés')

    def action_create(self):
        self.name.report_ids.unlink()
        for model in self.name.model_ids:
            report = self.env['dl.account.report.report'].create({
                'model_id' : model.id,
                'balance_id' : self.balance_id.id,
                'company_d'  : self.env.user.company_id.id,
                'name'       : model.name,
                'code'       : model.code + '-' + self.exercice
            })
            if not model.specifique:
                report.update_all()
            # else:
            #     if model.specifique_rep == '7_immo_cede':
            #         report.update_specifique7()
