# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import calendar
import math


class ParamG50(models.Model):
    _name    = 'account.g50.param'
    _description = 'Paramétrage G50'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order   = 'name'

    name    = fields.Char('Titre')
    state   = fields.Selection([('draft', 'Brouillon'), ('done', u'Validé')], string='Etat', default='draft')

    # data
    # tableau 1
    c1a11_brut = fields.Char('C1A11_Brut')
    c1a12_brut = fields.Char('C1A12_1')
    c1a13_brut = fields.Char('C1A13_1')
    c1a14_brut = fields.Char('C1A14_1')
    c1a20_brut = fields.Char('C1A20_1')
    c1a20_imp  = fields.Char('C1A20_2')

    # tableau 2
    t211        = fields.Char('E1M10_1')
    t212        = fields.Char('E1M10_2')
    t213        = fields.Char('E1M10_3')

    # tableau 3
    e1l20_imp        = fields.Char('E1L20_1')
    e1l20_retenu     = fields.Char('E1L20_3')
    e1l30_imp        = fields.Char('E1L30_1')
    e1l40_imp        = fields.Char('E1L40_1')
    e1l60_imp        = fields.Char('E1L60_1')
    e1l80_imp        = fields.Char('E1L80_1')
    e1l80_taux       = fields.Char('E1L80_2')
    e1m30_imp        = fields.Char('E1M30_1')
    e1m40_imp        = fields.Char('E1M40_1')
    e1m40_taux       = fields.Char('E1M40_2')

    # tableau 4
    e2e00_1_libelle        = fields.Char('E2E00_11')
    e2e00_1_imp        = fields.Char('E2E00_12')
    e2e00_1_taux        = fields.Char('E2E00_13')

    e2e00_2_libelle        = fields.Char('E2E00_21')
    e2e00_2_imp        = fields.Char('E2E00_22')
    e2e00_2_taux        = fields.Char('E2E00_23')

    e2e00_3_libelle        = fields.Char('E2E00_31')
    e2e00_3_imp        = fields.Char('E2E00_32')
    e2e00_3_taux        = fields.Char('E2E00_33')

    # tableau 5

    t511        = fields.Char('E2E05_11')
    t512        = fields.Char('E2E05_12')
    t513        = fields.Char('E2E05_13')

    t521        = fields.Char('E2E05_21')
    t522        = fields.Char('E2E05_22')
    t523        = fields.Char('E2E05_23')

    t531        = fields.Char('E2E05_31')
    t532        = fields.Char('E2E05_32')
    t533        = fields.Char('E2E05_33')

    # tableau 6
    t661        = fields.Char('661')           # TIC

    # tableau 7
    t711        = fields.Char('E3B11_1')
    t712        = fields.Char('E3B11_2')

    t721        = fields.Char('E3B12_1')
    t722        = fields.Char('E3B12_2')

    t731        = fields.Char('E3B13_1')
    t732        = fields.Char('E3B13_2')

    t741        = fields.Char('E3B14_1')
    t742        = fields.Char('E3B14_2')

    t751        = fields.Char('E3B15_1')
    t752        = fields.Char('E3B15_2')

    t761        = fields.Char('E3B16_1')
    t762        = fields.Char('E3B16_2')

    t771        = fields.Char('E3B21_1')
    t772        = fields.Char('E3B21_2')

    t781        = fields.Char('E3B22_1')
    t782        = fields.Char('E3B22_2')

    t791        = fields.Char('E3B23_1')
    t792        = fields.Char('E3B23_2')

    t7a1        = fields.Char('E3B24_1')
    t7a2        = fields.Char('E3B24_2')

    t7b1        = fields.Char('E3B25_1')
    t7b2        = fields.Char('E3B25_2')

    t7c1        = fields.Char('E3B26_1')
    t7c2        = fields.Char('E3B26_2')

    t7d1        = fields.Char('E3B28_1')
    t7d2        = fields.Char('E3B28_2')

    t7e1        = fields.Char('E3B31_1')
    t7e2        = fields.Char('E3B31_2')

    t7f1        = fields.Char('E3B32_1')
    t7f2        = fields.Char('E3B32_2')

    t7g1        = fields.Char('E3B33_1')
    t7g2        = fields.Char('E3B33_2')

    t7h1        = fields.Char('E3B34_1')
    t7h2        = fields.Char('E3B34_2')

    t7i1        = fields.Char('E3B35_1')
    t7i2        = fields.Char('E3B35_2')

    t7j1        = fields.Char('E3B36_1')
    t7j2        = fields.Char('E3B36_2')

    t7k1        = fields.Char('E3B37_1')
    t7k2        = fields.Char('E3B37_2')

    # tableau 8
    t811 = fields.Char('E3B91')
    t821 = fields.Char('E3B92')
    t831 = fields.Char('E3B91')
    t841 = fields.Char('E3B92')
    t851 = fields.Char('E3B91')
    t861 = fields.Char('E3B92')

    # tableau 9
    t921 = fields.Char('E3B97')
    t931 = fields.Char('E3B98')

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'
