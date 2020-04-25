# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import date


class Asset(models.Model):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'

    # cession
    cession_date    = fields.Date('Date cession')
    cession_montant = fields.Float('Montant cession')
    valeur_ammortissement = fields.Float('Ammortissement pratiqué')
    valeur_net = fields.Float('Valeur nette')
    cession = fields.Boolean(u'Cédé')

    def set_to_close(self):
        if self.value_residual > 0:
            self.cession_date = date.today()
            self.cession_montant = self.value_residual
            self.valeur_ammortissement = self.value - self.value_residual
            self.valeur_net = self.value_residual
            self.cession = True

        super(Asset, self).set_to_close()

# class AssetCategoryGroup(models.Model):
#     _name = 'account.asset.category.group'
#
#     name = fields.Char('Groupe')
#     parent_id = fields.Many2one('account.asset.category.group', string='Parent')
#
#
# class AssetCategory(models.Model):
#     _name = 'account.asset.category'
#     _inherit = 'account.asset.category'
#
#     code  = fields.Char('Code')
#     group_id = fields.Many2one('account.asset.category.group', string='Groupe')
