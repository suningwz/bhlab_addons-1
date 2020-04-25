# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _name    = 'account.journal'
    _inherit = 'account.journal'

    saisie = fields.Selection([('manual', u'Saisie autorisée'),
                               ('automatic', u'Généré automatiquement'), ], string='Type de saisie', default='manual')
