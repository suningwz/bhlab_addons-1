# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportsSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'reports.config.settings'

    default_journal_ch  = fields.Char(default_model='account.etat.tva', string='Journaux utilisés', help="""Codes journaux, séparés par des virules""")
    default_ht_inv_tva  = fields.Char(default_model='account.etat.tva', string='Comptes comptables pour les montants HT')
    default_tva_inv_tva = fields.Char(default_model='account.etat.tva', string='Comptes comptables pour les montants TVA')
    default_ht_ach_tva  = fields.Char(default_model='account.etat.tva', string='Comptes comptables pour les montants HT')
    default_tva_ach_tva = fields.Char(default_model='account.etat.tva', string='Comptes comptables pour les montants TVA')

    default_journal_104 = fields.Char(default_model='account.etat.client', string='Journaux utilisés', help="""Codes journaux, séparés par des virules""")
    default_ht_104      = fields.Char(default_model='account.etat.client', string='Comptes comptables pour les montants HT')
    default_tva_104     = fields.Char(default_model='account.etat.client', string='Comptes comptables pour les montants TVA')

    # default_journal_tap = fields.Char(default_model='account.etat.client', string='Journaux utilisés', help="""Codes journaux, séparés par des virules""")
    # default_ht_tap      = fields.Char(default_model='account.etat.client', string='Comptes comptables pour les montants HT')
    # default_tva_tap     = fields.Char(default_model='account.etat.client', string='Comptes comptables pour les montants TVA')
    default_tap_tap     = fields.Char(default_model='account.etat.tap', string='Comptes comptables pour les montants TAP')
