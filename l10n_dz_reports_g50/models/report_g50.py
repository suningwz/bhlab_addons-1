# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import calendar
import math


class DirectionImpot(models.Model):
    _name = 'direction.impot'
    _description = 'Direction generale des impots'

    name = fields.Char('Direction')
    inspection = fields.Char('Inspection des impots')
    recette    = fields.Char('Recette des impots')
    commune_id = fields.Many2one('res.commune', string='Commune')
    wilaya_id = fields.Many2one('res.country.state', string='Wilaya')

    phone = fields.Char('Téléphone')
    fax = fields.Char('Fax')
    mobile = fields.Char('Mobile')
    email = fields.Char('email')
    siteweb = fields.Char('Site web')


class ResCompany(models.Model):
    _inherit = 'res.company'

    dir_impot = fields.Many2one('direction.impot', string='direction des impots')


class AccountG50(models.Model):
    _name    = 'account.g50'
    _description = 'Etat G50'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order   = 'name'

    @api.model
    def _get_default_exercice(self):
        exe = self.env['account.exercice'].search([('defaut', '=', True)])
        if exe.exists():
            return exe[0].id
        else:
            return None

    name        = fields.Char('Titre', readonly=1)

    date       = fields.Date('Date', required=True, readonly=1, states={'draft': [('readonly', False)]})
    exercice_id = fields.Many2one('account.exercice', string='Exercice', required=True, default=_get_default_exercice,
                                  readonly=1, states={'draft': [('readonly', False)]})
    exercice = fields.Char(related='exercice_id.name', size=4, readonly=True)
    period_id  = fields.Many2one('account.exercice.period', string='Periode', required=True)
    mois       = fields.Selection(related='period_id.mois', string='Mois', required=True, readonly=1)

    impot_id   = fields.Many2one(related='company_id.dir_impot', string='Direction des impots', readonly=True)
    inspection = fields.Char(related='impot_id.inspection', string='Inspection des impots')
    recette    = fields.Char(related='impot_id.recette', string='Recette des impots')
    wilaya_id = fields.Many2one(related='impot_id.wilaya_id', string='Commune')
    commune_id = fields.Many2one(related='impot_id.commune_id', string='Commune')

    company_id = fields.Many2one('res.company', string='Raison sociale', default=lambda self: self.env.user.company_id.id, readonly=1, states={'draft': [('readonly', False)]})
    # adresse_id = fields.Char(related='company_id.get_address', string='Adresse')
    activite   = fields.Char(related='company_id.activite', string='Activité')
    nis        = fields.Char(related='company_id.nis', string='NIS')
    nif        = fields.Char(related='company_id.nif', string='NIF')
    ai         = fields.Char(related='company_id.ai', string='Article d\'imposition')

    state       = fields.Selection([('draft', 'Brouillon'), ('done', 'Terminé')], string='Etat', default='draft')
    notes       = fields.Text('Notes')
    param_id    = fields.Many2one('account.g50.param', string=u'Paramétrage', readonly=1, states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        period = self.env['account.exercice.period'].browse(vals['period_id'])
        if period.exists():
            vals['name'] = 'G50/' + period.name
        return super(AccountG50, self).create(vals)

    # data
    # tableau 1
    @api.multi
    @api.depends('c1a11_brut')
    def _compute_c1a11(self):
        for rec in self:
            rec.c1a11_imp = rec.c1a11_brut / 2
            rec.c1a11_mtn = rec.c1a11_imp * 0.02

    c1a11_brut = fields.Float('C1A11_Brut')
    c1a11_imp  = fields.Float(compute=_compute_c1a11, string='C1A11_Imp')
    c1a11_mtn  = fields.Float(compute=_compute_c1a11, string='C1A11_Mtn')

    @api.multi
    @api.depends('c1a12_brut')
    def _compute_c1a12(self):
        for rec in self:
            rec.c1a12_imp = rec.c1a12_brut * 0.7
            rec.c1a12_mtn = rec.c1a12_imp * 0.02

    c1a12_brut = fields.Float('C1A12_1')
    c1a12_imp  = fields.Float(compute=_compute_c1a12, string='C1A12_2')
    c1a12_mtn  = fields.Float(compute=_compute_c1a12, string='C1A12_3')

    @api.multi
    @api.depends('c1a13_brut')
    def _compute_c1a13(self):
        for rec in self:
            rec.c1a13_imp = rec.c1a13_brut
            rec.c1a13_mtn = rec.c1a13_brut * 0.02

    c1a13_brut        = fields.Float('C1A13_1')
    c1a13_imp        = fields.Float(compute=_compute_c1a13, string='C1A13_2')
    c1a13_mtn        = fields.Float(compute=_compute_c1a13, string='C1A13_3')

    @api.multi
    @api.depends('c1a14_brut')
    def _compute_c1a14(self):
        for rec in self:
            rec.c1a14_imp = rec.c1a14_brut
            rec.c1a14_mtn = rec.c1a14_brut * 0.02

    c1a14_brut = fields.Float('C1A14_1')
    c1a14_imp = fields.Float(compute=_compute_c1a14, string='C1A14_2')
    c1a14_mtn = fields.Float(compute=_compute_c1a14, string='C1A14_3')

    @api.multi
    @api.depends('c1a20_brut', 'c1a20_imp')
    def _compute_c1a20(self):
        for rec in self:
            rec.c1a20_mtn = (rec.c1a20_brut + rec.c1a20_imp) * 0.02

    c1a20_brut        = fields.Float('C1A20_1')
    c1a20_imp        = fields.Float('C1A20_2')
    c1a20_mtn        = fields.Float(compute=_compute_c1a20, string='C1A20_3')

    @api.multi
    @api.depends('c1a11_brut', 'c1a12_brut', 'c1a13_brut', 'c1a14_brut', 'c1a20_brut', 'c1a20_brut')
    def _compute_total1(self):
        for rec in self:
            rec.c1a_brut_total = rec.c1a11_brut + rec.c1a12_brut + rec.c1a13_brut + rec.c1a14_brut + rec.c1a20_brut
            rec.c1a_imp_total = rec.c1a11_imp + rec.c1a12_imp + rec.c1a13_imp + rec.c1a20_imp
            rec.c1a_mtn_total = rec.c1a11_mtn + rec.c1a12_mtn + rec.c1a13_mtn + rec.c1a20_mtn

    c1a_brut_total = fields.Float(compute=_compute_total1, string='total 11')
    c1a_imp_total = fields.Float(compute=_compute_total1, string='total 12')
    c1a_mtn_total = fields.Float(compute=_compute_total1, string='total 13')

    # tableau 2
    @api.multi
    @api.depends('t213')
    def _compute_total2(self):
        for rec in self:
            rec.t23 = rec.t213

    t211        = fields.Selection([('1er', '1er'), ('2eme', '2eme'), ('3eme', '3eme')], string='E1M10_1')
    t212        = fields.Char('E1M10_2')
    t213        = fields.Float('E1M10_3')

    t23         = fields.Float(compute=_compute_total2, string='total 23')

    # tableau 3
    e1l20_imp        = fields.Float('E1L20_1')
    e1l20_retenu        = fields.Float('E1L20_3')

    @api.multi
    @api.depends('e1l30_imp')
    def _compute_e1l30(self):
        for rec in self:
            rec.e1l30_retenu = rec.e1l30_imp * 0.1

    e1l30_imp        = fields.Float('E1L30_1')
    e1l30_retenu        = fields.Float(compute=_compute_e1l30, string='E1L30_3')

    @api.multi
    @api.depends('e1l40_imp')
    def _compute_e1l40(self):
        for rec in self:
            rec.e1l40_retenu = rec.e1l40_imp * 0.15

    e1l40_imp        = fields.Float('E1L40_1')
    e1l40_retenu        = fields.Float(compute=_compute_e1l40, string='E1L40_3')

    @api.multi
    @api.depends('e1l60_imp')
    def _compute_e1l60(self):
        for rec in self:
            rec.e1l60_retenu = rec.e1l60_imp * 0.5

    e1l60_imp        = fields.Float('E1L60_1')
    e1l60_retenu        = fields.Float(compute=_compute_e1l60, string='E1L60_3')

    @api.multi
    @api.depends('e1l80_imp', 'e1l80_taux')
    def _compute_e1l80(self):
        for rec in self:
            rec.e1l80_retenu = rec.e1l80_imp * rec.e1l80_taux / 100

    e1l80_imp        = fields.Float('E1L80_1')
    e1l80_taux        = fields.Float('E1L80_2')
    e1l80_retenu        = fields.Float(compute=_compute_e1l80, string='E1L80_3')

    @api.multi
    @api.depends('e1m30_retenu')
    def _compute_e1m30(self):
        for rec in self:
            rec.e1m30_retenu = rec.e1m30_imp * 0.24

    e1m30_imp        = fields.Float('E1M30_1')
    e1m30_retenu        = fields.Float(compute=_compute_e1l60, string='E1M30_3')

    @api.multi
    @api.depends('e1m40_imp', 'e1m40_taux')
    def _compute_e1m40(self):
        for rec in self:
            rec.e1m40_retenu = rec.e1m40_imp * rec.e1m40_taux / 100

    e1m40_imp        = fields.Float('E1M40_1')
    e1m40_taux        = fields.Float('E1M40_2')
    e1m40_retenu        = fields.Float(compute=_compute_e1m40, string='E1M40_3')

    @api.multi
    @api.depends('e1l20_imp', 'e1l30_imp', 'e1l40_imp', 'e1l60_imp', 'e1l80_imp', 'e1m30_imp', 'e1m40_imp')
    def _compute_total3_imp(self):
        for rec in self:
            rec.tab3_total_imp = rec.e1l20_imp + rec.e1l30_imp + rec.e1l40_imp + rec.e1l60_imp + rec.e1l80_imp + rec.e1m30_imp + rec.e1m40_imp

    @api.multi
    @api.depends('e1l20_retenu', 'e1l30_retenu', 'e1l40_retenu', 'e1l60_retenu', 'e1l80_retenu', 'e1m30_retenu', 'e1m40_retenu')
    def _compute_total3_retenu(self):
        for rec in self:
            rec.tab3_total_retenu = rec.e1l20_retenu + rec.e1l30_retenu + rec.e1l40_retenu + rec.e1l60_retenu + rec.e1l80_retenu + rec.e1m30_retenu + rec.e1m40_retenu

    tab3_total_imp    = fields.Float(compute=_compute_total3_imp, string='total 31')
    tab3_total_retenu = fields.Float(compute=_compute_total3_retenu, string='total 33')

    # tableau 4
    @api.multi
    @api.depends('e2e00_1_imp', 'e2e00_1_taux')
    def _compute_e2e00_1(self):
        for rec in self:
            rec.e2e00_1_a_payer = rec.e2e00_1_imp * rec.e2e00_1_taux / 100

    e2e00_1_libelle = fields.Char('E2E00_11')
    e2e00_1_imp     = fields.Float('E2E00_12')
    e2e00_1_taux    = fields.Float('E2E00_13')
    e2e00_1_a_payer = fields.Float(compute=_compute_e2e00_1, string='E2E00_14')

    @api.multi
    @api.depends('e2e00_2_imp', 'e2e00_2_taux')
    def _compute_e2e00_2(self):
        for rec in self:
            rec.e2e00_2_a_payer = rec.e2e00_2_imp * rec.e2e00_2_taux / 100

    e2e00_2_libelle = fields.Char('E2E00_21')
    e2e00_2_imp     = fields.Float('E2E00_22')
    e2e00_2_taux    = fields.Float('E2E00_23')
    e2e00_2_a_payer = fields.Float(compute=_compute_e2e00_2, string='E2E00_24')

    @api.multi
    @api.depends('e2e00_3_imp', 'e2e00_3_taux')
    def _compute_e2e00_3(self):
        for rec in self:
            rec.e2e00_3_a_payer = rec.e2e00_3_imp * rec.e2e00_3_taux / 100

    e2e00_3_libelle = fields.Char('E2E00_31')
    e2e00_3_imp     = fields.Float('E2E00_32')
    e2e00_3_taux    = fields.Float('E2E00_33')
    e2e00_3_a_payer = fields.Float(compute=_compute_e2e00_3, string='E2E00_34')

    @api.multi
    @api.depends('e2e00_1_imp', 'e2e00_2_imp', 'e2e00_3_imp')
    def _compute_total4_imp(self):
        for rec in self:
            rec.tab4_total_imp = rec.e2e00_1_imp + rec.e2e00_2_imp + rec.e2e00_3_imp

    @api.multi
    @api.depends('e2e00_1_a_payer', 'e2e00_2_a_payer', 'e2e00_3_a_payer')
    def _compute_total4_a_payer(self):
        for rec in self:
            rec.tab4_total_a_payer = rec.e2e00_1_a_payer + rec.e2e00_2_a_payer + rec.e2e00_3_a_payer

    tab4_total_imp     = fields.Float(compute=_compute_total4_imp, string='total 42')
    tab4_total_a_payer = fields.Float(compute=_compute_total4_a_payer, string='total 44')

    # tableau 5
    @api.multi
    @api.depends('t512', 't513')
    def _compute_e2e05_1(self):
        for rec in self:
            rec.t514 = rec.t512 * rec.t513 / 100

    t511        = fields.Char('E2E05_11')
    t512        = fields.Float('E2E05_12')
    t513        = fields.Float('E2E05_13')
    t514        = fields.Float(compute=_compute_e2e05_1, string='E2E05_14')

    @api.multi
    @api.depends('t522', 't523')
    def _compute_e2e05_2(self):
        for rec in self:
            rec.t524 = rec.t522 * rec.t523 / 100

    t521        = fields.Char('E2E05_21')
    t522        = fields.Float('E2E05_22')
    t523        = fields.Float('E2E05_23')
    t524        = fields.Float(compute=_compute_e2e05_2, string='E2E05_24')

    @api.multi
    @api.depends('t532', 't533')
    def _compute_e2e05_3(self):
        for rec in self:
            rec.t534 = rec.t532 * rec.t533 / 100

    t531        = fields.Char('E2E05_31')
    t532        = fields.Float('E2E05_32')
    t533        = fields.Float('E2E05_33')
    t534        = fields.Float(compute=_compute_e2e05_3, string='E2E05_34')

    @api.multi
    @api.depends('t512', 't522', 't532', 't514', 't524', 't534')
    def _compute_total5(self):
        for rec in self:
            rec.t52 = rec.t512 + rec.t522 + rec.t532
            rec.t54 = rec.t514 + rec.t524 + rec.t534

    t52         = fields.Float(compute=_compute_total5, string='total 52')
    t54         = fields.Float(compute=_compute_total5, string='total 54')

    # tableau 6
    @api.multi
    @api.depends('t611', 't621', 't631', 't641', 't651', 't661', 't671', 't681', 't691')
    def _compute_total_6(self):
        for rec in self:
            rec.t61 = rec.t611 + rec.t621 + rec.t631 + rec.t641 + rec.t651 + rec.t661 + rec.t671 + rec.t681 + rec.t691

    t611        = fields.Float(related='c1a_mtn_total')   # TAP
    t621        = fields.Float(related='t23')   # IBS
    t631        = fields.Float(related='e1l20_retenu')  # IRG Salaire
    t641        = fields.Float(related='e1l80_retenu')  # IRG / Autres ret. sources
    t651        = fields.Float(related='e1m40_retenu')  # IBS / Ret. a la source
    t661        = fields.Float('661')           # TIC
    t671        = fields.Float(related='tab4_total_a_payer')   # droit et timbre
    t681        = fields.Float(related='t54')   # autre
    t691        = fields.Float(related='t961', string='661')           # TVA - a recalculer

    t61        = fields.Float(compute=_compute_total_6, string='t61')

    # tableau 7
    @api.multi
    @api.depends('t711', 't712')
    def _compute_71_3_4(self):
        for rec in self:
            rec.t713 = rec.t711 - rec.t712
            rec.t714 = rec.t713 * 0.09

    t711        = fields.Float('E3B11_1')
    t712        = fields.Float('E3B11_2')
    t713        = fields.Float(compute=_compute_71_3_4, string='E3B11_3')
    t714        = fields.Float(compute=_compute_71_3_4, string='E3B11_4')

    @api.multi
    @api.depends('t721', 't722')
    def _compute_72_3_4(self):
        for rec in self:
            rec.t723 = rec.t721 - rec.t722
            rec.t724 = rec.t723 * 0.09

    t721        = fields.Float('E3B12_1')
    t722        = fields.Float('E3B12_2')
    t723        = fields.Float(compute=_compute_72_3_4, string='E3B12_3')
    t724        = fields.Float(compute=_compute_72_3_4, string='E3B12_4')

    @api.multi
    @api.depends('t731', 't732')
    def _compute_73_3_4(self):
        for rec in self:
            rec.t733 = rec.t731 - rec.t732
            rec.t734 = rec.t733 * 0.09

    t731        = fields.Float('E3B13_1')
    t732        = fields.Float('E3B13_2')
    t733        = fields.Float(compute=_compute_73_3_4, string='E3B13_3')
    t734        = fields.Float(compute=_compute_73_3_4, string='E3B13_4')

    @api.multi
    @api.depends('t741', 't742')
    def _compute_74_3_4(self):
        for rec in self:
            rec.t743 = rec.t741 - rec.t742
            rec.t744 = rec.t743 * 0.09

    t741        = fields.Float('E3B14_1')
    t742        = fields.Float('E3B14_2')
    t743        = fields.Float(compute=_compute_74_3_4, string='E3B14_3')
    t744        = fields.Float(compute=_compute_74_3_4, string='E3B14_4')

    @api.multi
    @api.depends('t751', 't752')
    def _compute_75_3_4(self):
        for rec in self:
            rec.t753 = rec.t751 - rec.t752
            rec.t754 = rec.t753 * 0.09

    t751        = fields.Float('E3B15_1')
    t752        = fields.Float('E3B15_2')
    t753        = fields.Float(compute=_compute_75_3_4, string='E3B15_3')
    t754        = fields.Float(compute=_compute_75_3_4, string='E3B15_4')

    @api.multi
    @api.depends('t761', 't762')
    def _compute_76_3_4(self):
        for rec in self:
            rec.t763 = rec.t761 - rec.t762
            rec.t764 = rec.t763 * 0.09

    t761        = fields.Float('E3B16_1')
    t762        = fields.Float('E3B16_2')
    t763        = fields.Float(compute=_compute_76_3_4, string='E3B16_3')
    t764        = fields.Float(compute=_compute_76_3_4, string='E3B16_4')

    @api.multi
    @api.depends('t771', 't772')
    def _compute_77_3_4(self):
        for rec in self:
            rec.t773 = rec.t771 - rec.t772
            rec.t774 = rec.t773 * 0.19

    t771        = fields.Float('E3B21_1')
    t772        = fields.Float('E3B21_2')
    t773        = fields.Float(compute=_compute_77_3_4, string='E3B21_3')
    t774        = fields.Float(compute=_compute_77_3_4, string='E3B21_4')

    @api.multi
    @api.depends('t781', 't782')
    def _compute_78_3_4(self):
        for rec in self:
            rec.t783 = rec.t781 - rec.t782
            rec.t784 = rec.t783 * 0.19

    t781        = fields.Float('E3B22_1')
    t782        = fields.Float('E3B22_2')
    t783        = fields.Float(compute=_compute_78_3_4, string='E3B22_3')
    t784        = fields.Float(compute=_compute_78_3_4, string='E3B22_4')

    @api.multi
    @api.depends('t791', 't792')
    def _compute_79_3_4(self):
        for rec in self:
            rec.t793 = rec.t791 - rec.t792
            rec.t794 = rec.t793 * 0.19

    t791        = fields.Float('E3B23_1')
    t792        = fields.Float('E3B23_2')
    t793        = fields.Float(compute=_compute_79_3_4, string='E3B23_3')
    t794        = fields.Float(compute=_compute_79_3_4, string='E3B23_4')

    @api.multi
    @api.depends('t7a1', 't7a2')
    def _compute_7a_3_4(self):
        for rec in self:
            rec.t7a3 = rec.t7a1 - rec.t7a2
            rec.t7a4 = rec.t7a3 * 0.19

    t7a1        = fields.Float('E3B24_1')
    t7a2        = fields.Float('E3B24_2')
    t7a3        = fields.Float(compute=_compute_7a_3_4, string='E3B24_3')
    t7a4        = fields.Float(compute=_compute_7a_3_4, string='E3B24_4')

    @api.multi
    @api.depends('t7b1', 't7b2')
    def _compute_7b_3_4(self):
        for rec in self:
            rec.t7b3 = rec.t7b1 - rec.t7b2
            rec.t7b4 = rec.t7b3 * 0.19

    t7b1        = fields.Float('E3B25_1')
    t7b2        = fields.Float('E3B25_2')
    t7b3        = fields.Float(compute=_compute_7b_3_4, string='E3B25_3')
    t7b4        = fields.Float(compute=_compute_7b_3_4, string='E3B25_4')

    @api.multi
    @api.depends('t7c1', 't7c2')
    def _compute_7c_3_4(self):
        for rec in self:
            rec.t7c3 = rec.t7c1 - rec.t7c2
            rec.t7c4 = rec.t7c3 * 0.19

    t7c1        = fields.Float('E3B26_1')
    t7c2        = fields.Float('E3B26_2')
    t7c3        = fields.Float(compute=_compute_7c_3_4, string='E3B25_3')
    t7c4        = fields.Float(compute=_compute_7c_3_4, string='E3B25_4')

    @api.multi
    @api.depends('t7d1', 't7d2')
    def _compute_7d_3_4(self):
        for rec in self:
            rec.t7d3 = rec.t7d1 - rec.t7d2
            rec.t7d4 = rec.t7d3 * 0.19

    t7d1        = fields.Float('E3B28_1')
    t7d2        = fields.Float('E3B28_2')
    t7d3        = fields.Float(compute=_compute_7d_3_4, string='E3B28_3')
    t7d4        = fields.Float(compute=_compute_7d_3_4, string='E3B28_4')

    @api.multi
    @api.depends('t7e1', 't7e2')
    def _compute_7e_3_4(self):
        for rec in self:
            rec.t7e3 = rec.t7e1 - rec.t7e2
            rec.t7e4 = rec.t7e3 * 0.19

    t7e1        = fields.Float('E3B31_1')
    t7e2        = fields.Float('E3B31_2')
    t7e3        = fields.Float(compute=_compute_7e_3_4, string='E3B31_3')
    t7e4        = fields.Float(compute=_compute_7e_3_4, string='E3B31_4')

    @api.multi
    @api.depends('t7f1', 't7f2')
    def _compute_7f_3_4(self):
        for rec in self:
            rec.t7f3 = rec.t7f1 - rec.t7f2
            rec.t7f4 = rec.t7f3 * 0.19

    t7f1        = fields.Float('E3B32_1')
    t7f2        = fields.Float('E3B32_2')
    t7f3        = fields.Float(compute=_compute_7f_3_4, string='E3B32_3')
    t7f4        = fields.Float(compute=_compute_7f_3_4, string='E3B32_4')

    @api.multi
    @api.depends('t7g1', 't7g2')
    def _compute_7g_3_4(self):
        for rec in self:
            rec.t7g3 = rec.t7g1 - rec.t7g2
            rec.t7g4 = rec.t7g3 * 0.19

    t7g1        = fields.Float('E3B33_1')
    t7g2        = fields.Float('E3B33_2')
    t7g3        = fields.Float(compute=_compute_7g_3_4, string='E3B33_3')
    t7g4        = fields.Float(compute=_compute_7g_3_4, string='E3B33_4')

    @api.multi
    @api.depends('t7h1', 't7h2')
    def _compute_7h_3_4(self):
        for rec in self:
            rec.t7h3 = rec.t7h1 - rec.t7h2
            rec.t7h4 = rec.t7h3 * 0.19

    t7h1        = fields.Float('E3B34_1')
    t7h2        = fields.Float('E3B34_2')
    t7h3        = fields.Float(compute=_compute_7h_3_4, string='E3B34_3')
    t7h4        = fields.Float(compute=_compute_7h_3_4, string='E3B34_4')

    @api.multi
    @api.depends('t7i1', 't7i2')
    def _compute_7i_3_4(self):
        for rec in self:
            rec.t7i3 = rec.t7i1 - rec.t7i2
            rec.t7i4 = rec.t7i3 * 0.19

    t7i1        = fields.Float('E3B35_1')
    t7i2        = fields.Float('E3B35_2')
    t7i3        = fields.Float(compute=_compute_7i_3_4, string='E3B35_3')
    t7i4        = fields.Float(compute=_compute_7i_3_4, string='E3B35_4')

    @api.multi
    @api.depends('t7j1', 't7j2')
    def _compute_7j_3_4(self):
        for rec in self:
            rec.t7j3 = rec.t7j1 - rec.t7j2
            rec.t7j4 = rec.t7j3 * 0.19

    t7j1        = fields.Float('E3B36_1')
    t7j2        = fields.Float('E3B36_2')
    t7j3        = fields.Float(compute=_compute_7j_3_4, string='E3B36_3')
    t7j4        = fields.Float(compute=_compute_7j_3_4, string='E3B36_4')

    @api.multi
    @api.depends('t7k1', 't7k2')
    def _compute_7k_3_4(self):
        for rec in self:
            rec.t7k3 = rec.t7k1 - rec.t7k2
            rec.t7k4 = rec.t7k3 * 0.19

    t7k1        = fields.Float('E3B37_1')
    t7k2        = fields.Float('E3B37_2')
    t7k3        = fields.Float(compute=_compute_7k_3_4, string='E3B37_3')
    t7k4        = fields.Float(compute=_compute_7k_3_4, string='E3B37_4')

    @api.multi
    @api.depends('t711', 't721', 't731', 't741', 't751', 't761', 't771', 't781', 't791', 't7a1', 't7b1', 't7c1', 't7d1', 't7e1', 't7f1', 't7g1', 't7h1', 't7i1', 't7j1', 't7k1')
    def _compute_total7_1(self):
        for rec in self:
            rec.t71 = rec.t711 + rec.t721 + rec.t731 + rec.t741 + rec.t751 + rec.t761 + rec.t771 + rec.t781 + rec.t791 + rec.t7a1 + rec.t7b1 + rec.t7c1 + rec.t7d1 + rec.t7e1 + rec.t7f1 + rec.t7g1 + rec.t7h1 + rec.t7i1 + rec.t7j1 + rec.t7k1

    @api.multi
    @api.depends('t712', 't722', 't732', 't742', 't752', 't762', 't772', 't782', 't792', 't7a2', 't7b2', 't7c2', 't7d2', 't7e2', 't7f2', 't7g2', 't7h2', 't7i2', 't7j2', 't7k2')
    def _compute_total7_2(self):
        for rec in self:
            rec.t72 = rec.t712 + rec.t722 + rec.t732 + rec.t742 + rec.t752 + rec.t762 + rec.t772 + rec.t782 + rec.t792 + rec.t7a2 + rec.t7b2 + rec.t7c2 + rec.t7d2 + rec.t7e2 + rec.t7f2 + rec.t7g2 + rec.t7h2 + rec.t7i2 + rec.t7j2 + rec.t7k2

    @api.multi
    @api.depends('t713', 't723', 't733', 't743', 't753', 't763', 't773', 't783', 't793', 't7a3', 't7b3', 't7c3', 't7d3', 't7e3', 't7f3', 't7g3', 't7h3', 't7i3', 't7j3', 't7k3')
    def _compute_total7_3(self):
        for rec in self:
            rec.t73 = rec.t713 + rec.t723 + rec.t733 + rec.t743 + rec.t753 + rec.t763 + rec.t773 + rec.t783 + rec.t793 + rec.t7a3 + rec.t7b3 + rec.t7c3 + rec.t7d3 + rec.t7e3 + rec.t7f3 + rec.t7g3 + rec.t7h3 + rec.t7i3 + rec.t7j3 + rec.t7k3

    @api.multi
    @api.depends('t714', 't724', 't734', 't744', 't754', 't764', 't774', 't784', 't794', 't7a4', 't7b4', 't7c4', 't7d4', 't7e4', 't7f4', 't7g4', 't7h4', 't7i4', 't7j4', 't7k4')
    def _compute_total7_4(self):
        for rec in self:
            rec.t74 = rec.t714 + rec.t724 + rec.t734 + rec.t744 + rec.t754 + rec.t764 + rec.t774 + rec.t784 + rec.t794 + rec.t7a4 + rec.t7b4 + rec.t7c4 + rec.t7d4 + rec.t7e4 + rec.t7f4 + rec.t7g4 + rec.t7h4 + rec.t7i4 + rec.t7j4 + rec.t7k4

    t71         = fields.Float(compute=_compute_total7_1, string='total 71')
    t72         = fields.Float(compute=_compute_total7_2, string='total 72')
    t73         = fields.Float(compute=_compute_total7_3, string='total 73')
    t74         = fields.Float(compute=_compute_total7_4, string='total 74')

    # tableau 8
    t811 = fields.Float('E3B91')
    t821 = fields.Float('E3B92')
    t831 = fields.Float('E3B91')
    t841 = fields.Float('E3B92')
    t851 = fields.Float('E3B91')
    t861 = fields.Float('E3B92')

    @api.multi
    @api.depends('t811', 't821', 't831', 't841', 't851', 't861')
    def _compute_total8(self):
        for rec in self:
            rec.t81 = rec.t811 + rec.t821 + rec.t831 + rec.t841 + rec.t851 + rec.t861

    t81 = fields.Float(compute=_compute_total8, string='total 81')

    # tableau 9
    @api.multi
    @api.depends('t911', 't921', 't931')
    def _compute_total9_c(self):
        for rec in self:
            rec.t941 = rec.t911 + rec.t921 + rec.t931

    @api.multi
    @api.depends('t941', 't81')
    def _compute_total9_6_7(self):
        for rec in self:
            if rec.t941 > rec.t81:
                rec.t961 = rec.t941 - rec.t81
                rec.t971 = 0.0
            else:
                rec.t961 = 0.0
                rec.t971 = rec.t81 - rec.t941

    t911 = fields.Float(related='t74', string='C')
    t921 = fields.Float('E3B97')
    t931 = fields.Float('E3B98')
    t941 = fields.Float(compute=_compute_total9_c, string='Total C')
    t951 = fields.Float(related='t81', string='B')
    t961 = fields.Float(compute=_compute_total9_6_7, string='E3B00')
    t971 = fields.Float(compute=_compute_total9_6_7, string='E3B99')

    # fonctions
    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    # @api.one
    # def compute_g50(self):
    #     def get_formule(var):
    #         ln = self.env['account.g50.param.line'].search([('name', '=', var), ('g50param_id', '=', self.param_id.id)])
    #         if ln.exists():
    #             if ln.formula_ch:
    #                 return ln.formula_ch
    #             else:
    #                 return None
    #         else:
    #             return None
    #
    #     def get_journaux(var):
    #         ln = self.env['account.g50.param.line'].search([('name', '=', var), ('g50param_id', '=', self.param_id.id)])
    #         if ln.exists():
    #             if ln.journal_ch:
    #                 lst = ln.journal_ch.split(",")
    #                 list_j = ''
    #                 for jrn in lst:
    #                     journal = self.env['account.journal'].search([('code', '=', jrn)])
    #                     if journal.exists():
    #                         list_j += str(journal.id) + ','
    #                 return list_j[:-1]
    #             else:
    #                 return ''
    #         else:
    #             return ''
    #
    #     def get_cpt(str_cpt):
    #         if not str_cpt.replace('.', '', 1).isdigit():
    #             if str_cpt[1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
    #                 return str_cpt[1:]
    #             else:
    #                 return str_cpt[2:]
    #         else:
    #             return str_cpt
    #
    #     def get_sens(str_cpt):
    #         if not str_cpt.replace('.', '', 1).isdigit():
    #             if str_cpt[1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
    #                 return str_cpt[:1]
    #             else:
    #                 return str_cpt[:2]
    #         else:
    #             return ''
    #
    #     def operation(mtn1, mtn2, op):
    #         if op == '+':
    #             return mtn1 + mtn2
    #         if op == '-':
    #             return mtn1 - mtn2
    #         if op == '*':
    #             return mtn1 * mtn2
    #         if op == '/':
    #             if mtn2 != 0.0:
    #                 return mtn1 / mtn2
    #             else:
    #                 return mtn1
    #
    #     def get_account_amount(account, sens, date_1, date_2, lst_journal):
    #         if sens == '':  # un nombre
    #             return float(account)
    #         else:
    #             req = "select sum(debit) as debit, sum(credit) as credit " \
    #                   "from account_move_line, account_account, account_move " \
    #                   "where account_account.id = account_move_line.account_id and account_move_line.move_id = account_move.id " \
    #                   "and account_account.code like %s " \
    #                   "and account_move.date between %s and %s "
    #             if lst_journal != '':
    #                 req += 'and account_move.journal_id in (' + lst_journal + ');'
    #             else:
    #                 req += ';'
    #             rub = (account + '%', date_1, date_2)
    #             self._cr.execute(req, rub)
    #             res = self._cr.dictfetchall()
    #
    #             deb = 0.0
    #             cre = 0.0
    #             if res[0].get('credit'):
    #                 cre = res[0].get('credit')
    #             if res[0].get('debit'):
    #                 deb = res[0].get('debit')
    #
    #             if sens == 'C':
    #                 return cre
    #             if sens == 'D':
    #                 return deb
    #             if sens == 'SD':
    #                 return deb - cre
    #             if sens == 'SC':
    #                 return cre - deb
    #
    #     def compute_field(fld):
    #         formula = get_formule(fld.name)
    #         if formula:
    #             lst = []
    #             m = ''
    #             for i in range(0, len(formula)):
    #                 # print formule[i]
    #
    #                 if formula[i] not in ('+', '-', '(', ')', '*', '/'):
    #                     m += formula[i]
    #                 else:
    #                     if m: lst.append(m)
    #                     lst.append(formula[i])
    #                     m = ''
    #             lst.append(m)
    #             # print lst
    #
    #             # calculer et convertir les comptes de la liste en montants
    #             lst_mtn = []
    #             for var in lst:
    #                 if var not in ('+', '-', '(', ')', '*', '/'):
    #                     lst_mtn.append(get_account_amount(get_cpt(var), get_sens(var), date1, date2, get_journaux(fld.name)))
    #                 else:
    #                     lst_mtn.append(var)
    #             # print lst_mtn
    #
    #             # faire le calcul
    #             i = 0
    #             montant = 0.0
    #             operateur = '+'
    #             for var in lst_mtn:
    #                 if var:
    #                     if var not in ('+', '-', '(', ')', '*', '/'):
    #                         if i == 0:
    #                             montant = var
    #                             i += 1
    #                         else:
    #                             montant = operation(montant, var, operateur)
    #                     else:
    #                         if var not in ('(', ')'):
    #                             operateur = var
    #             # print montant
    #             # return int(montant)
    #             if fld.arrondi:
    #                 return math.floor(montant / 10) * 10
    #             else:
    #                 return montant
    #         else:
    #             if fld.value:
    #                 if fld.type_value == 'int':
    #                     return int(fld.value)
    #                 if fld.type_value == 'float':
    #                     return float(fld.value)
    #                 if fld.type_value == 'str':
    #                     return str(fld.value)
    #
    #     if self.param_id:
    #         date1 = '01-' + self.mois + '-' + self.exercice
    #         date2 = str(calendar.monthrange(int(self.exercice), int(self.mois))[1])+'-' + self.mois + '-' + self.exercice
    #
    #         for flds in self.param_id.line_ids:  # parcourir toutes les variables (tabc, ...) et faire le calcul
    #             self.write({flds.name : compute_field(flds)})

    def total_compte(self, account, debit_credit, operation=1):
        # debit et credit initial
        req = "select sum(debit) as debit, sum(credit) as credit " \
              "from account_move_line, account_account, account_move " \
              "where account_account.id = account_move_line.account_id and account_move_line.move_id = account_move.id " \
              "and account_account.code like %s " \
              "and account_move.date between %s and %s;"
        # if lst_journal != '':
        #     req += 'and account_move.journal_id in (' + lst_journal + ');'
        # else:
        #     req += ';'
        rub = (account + '%', self.period_id.date_debut, self.period_id.date_fin)
        self._cr.execute(req, rub)
        res = self._cr.dictfetchall()

        credit = 0.0
        debit  = 0.0
        if res[0].get('credit'):
            credit = res[0].get('credit')
        if res[0].get('debit'):
            debit = res[0].get('debit')

        if debit_credit == 'C':
            return operation * credit
        elif debit_credit == 'D':
            return operation * debit
        elif debit_credit == 'SC':
            return operation * (credit - debit)
        elif debit_credit == 'SD':
            return operation * (debit - credit)

    def calcul_elem(self, elem, periode='N'):
        # Opérateur
        operateur = 1
        if elem[:1] == '-':
            operateur = -1
            elem = elem[1:]

        # Calcul
        if elem[:2] in ('SC', 'SD', 'SX'):
            oper = elem[:2]
            compte = elem[2:]
            return self.total_compte(compte, oper, operateur)
        else:
            if elem[:1] in ('C', 'D', 'V'):
                oper = elem[:1]
                compte = elem[1:]
                return self.total_compte(compte, oper, operateur)
            else:
                if elem[:1].isdigit():
                    oper = 'SX'
                    compte = elem
                    return self.total_compte(compte, oper, operateur)
                else:
                    return 0

    def compute_amount(self, formule_str):
        def operation(mtn1, mtn2, op):
            if op == '+':
                return mtn1 + mtn2
            if op == '-':
                return mtn1 - mtn2
            if op == '*':
                return mtn1 * mtn2
            if op == '/':
                if mtn2 != 0.0:
                    return mtn1 / mtn2
                else:
                    return mtn1

        if formule_str:
            # récupération de la formule
            lst = []
            m = ''
            for i in range(0, len(formule_str)):
                # print formule[i]
                if formule_str[i] not in ('+', '-', '(', ')', '*', '/'):
                    m += formule_str[i]
                else:
                    if m: lst.append(m)
                    lst.append(formule_str[i])
                    m = ''
            lst.append(m)
            print(lst)

            lst_mtn = []
            for var in lst:
                # calculer et convertir les comptes de la liste en montants
                if var not in ('+', '-', '(', ')', '*', '/'):
                    lst_mtn.append(self.calcul_elem(var))
                else:
                    lst_mtn.append(var)
            print(lst_mtn)

            # faire le calcul
            i = 0
            tot = 0.0
            operator = '+'
            for var in lst_mtn:
                if var:
                    if var not in ('+', '-', '(', ')', '*', '/'):
                        if i == 0:
                            tot = var
                            i += 1
                        else:
                            tot = operation(tot, var, operator)
                    else:
                        if var not in ('(', ')'):
                            operator = var
                            i += 1
            print(tot)

            return tot
        else:
            return 0.0

    def load_data(self):
        self.c1a11_brut = self.compute_amount(self.param_id.c1a11_brut) # / self.devise_id.division
        self.c1a12_brut = self.compute_amount(self.param_id.c1a12_brut) # / self.devise_id.division
        self.c1a13_brut = self.compute_amount(self.param_id.c1a13_brut) # / self.devise_id.division
        self.c1a14_brut = self.compute_amount(self.param_id.c1a14_brut)
        self.c1a20_brut = self.compute_amount(self.param_id.c1a20_brut)
        self.c1a20_imp  = self.compute_amount(self.param_id.c1a20_imp)

        self.t212         = self.param_id.t212
        self.t213         = self.compute_amount(self.param_id.t213)
        self.e1l20_imp    = self.compute_amount(self.param_id.e1l20_imp)
        self.e1l20_retenu = self.compute_amount(self.param_id.e1l20_retenu)
        self.e1l30_imp    = self.compute_amount(self.param_id.e1l30_imp)
        self.e1l40_imp    = self.compute_amount(self.param_id.e1l40_imp)
        self.e1l60_imp    = self.compute_amount(self.param_id.e1l60_imp)
        self.e1l80_imp    = self.compute_amount(self.param_id.e1l80_imp)
        self.e1l80_taux   = self.compute_amount(self.param_id.e1l80_taux)
        self.e1m30_imp    = self.compute_amount(self.param_id.e1m30_imp)
        self.e1m40_imp    = self.compute_amount(self.param_id.e1m40_imp)
        self.e1m40_taux   = self.compute_amount(self.param_id.e1m40_taux)
        self.e2e00_1_libelle = self.param_id.e2e00_1_libelle
        self.e2e00_1_imp  = self.compute_amount(self.param_id.e2e00_1_imp)
        self.e2e00_1_taux = self.compute_amount(self.param_id.e2e00_1_taux)
        self.e2e00_2_libelle = self.param_id.e2e00_2_libelle
        self.e2e00_2_imp  = self.compute_amount(self.param_id.e2e00_2_imp)
        self.e2e00_2_taux = self.compute_amount(self.param_id.e2e00_2_taux)
        self.e2e00_3_libelle = self.param_id.e2e00_3_libelle
        self.e2e00_3_imp  = self.compute_amount(self.param_id.e2e00_3_imp)
        self.e2e00_3_taux = self.compute_amount(self.param_id.e2e00_3_taux)
# t511
        self.t511 = self.param_id.t511
        self.t512 = self.compute_amount(self.param_id.t512)
        self.t513 = self.compute_amount(self.param_id.t513)
        self.t521 = self.param_id.t521
        self.t522 = self.compute_amount(self.param_id.t522)
        self.t523 = self.compute_amount(self.param_id.t523)
        self.t531 = self.param_id.t531
        self.t532 = self.compute_amount(self.param_id.t532)
        self.t533 = self.compute_amount(self.param_id.t533)
        self.t661 = self.compute_amount(self.param_id.t661)         # TIC

        self.t711        = self.compute_amount(self.param_id.t711)
        self.t712        = self.compute_amount(self.param_id.t712)
        self.t731        = self.compute_amount(self.param_id.t731)
        self.t732        = self.compute_amount(self.param_id.t732)
        self.t741        = self.compute_amount(self.param_id.t741)
        self.t742        = self.compute_amount(self.param_id.t742)
        self.t751        = self.compute_amount(self.param_id.t751)
        self.t752        = self.compute_amount(self.param_id.t752)
        self.t761        = self.compute_amount(self.param_id.t761)
        self.t762        = self.compute_amount(self.param_id.t762)
        self.t771        = self.compute_amount(self.param_id.t771)
        self.t772        = self.compute_amount(self.param_id.t772)
        self.t781        = self.compute_amount(self.param_id.t781)
        self.t782        = self.compute_amount(self.param_id.t782)
        self.t791        = self.compute_amount(self.param_id.t791)
        self.t792        = self.compute_amount(self.param_id.t792)
        self.t7a1        = self.compute_amount(self.param_id.t7a1)
        self.t7a2        = self.compute_amount(self.param_id.t7a2)
        self.t7b1        = self.compute_amount(self.param_id.t7b1)
        self.t7b2        = self.compute_amount(self.param_id.t7b2)
        self.t7c1        = self.compute_amount(self.param_id.t7c1)
        self.t7c2        = self.compute_amount(self.param_id.t7c2)
        self.t7d1        = self.compute_amount(self.param_id.t7d1)
        self.t7d2        = self.compute_amount(self.param_id.t7d2)
        self.t7e1        = self.compute_amount(self.param_id.t7e1)
        self.t7e2        = self.compute_amount(self.param_id.t7e2)
        self.t7f1        = self.compute_amount(self.param_id.t7f1)
        self.t7f2        = self.compute_amount(self.param_id.t7f2)
        self.t7g1        = self.compute_amount(self.param_id.t7g1)
        self.t7g2        = self.compute_amount(self.param_id.t7g2)
        self.t7h1        = self.compute_amount(self.param_id.t7h1)
        self.t7h2        = self.compute_amount(self.param_id.t7h2)
        self.t7i1        = self.compute_amount(self.param_id.t7i1)
        self.t7i2        = self.compute_amount(self.param_id.t7i2)
        self.t7j1        = self.compute_amount(self.param_id.t7j1)
        self.t7j2        = self.compute_amount(self.param_id.t7j2)
        self.t7k1        = self.compute_amount(self.param_id.t7k1)
        self.t7k2        = self.compute_amount(self.param_id.t7k2)
    # tableau 8
        self.t811 = self.compute_amount(self.param_id.t811)
        self.t821 = self.compute_amount(self.param_id.t821)
        self.t831 = self.compute_amount(self.param_id.t831)
        self.t841 = self.compute_amount(self.param_id.t841)
        self.t851 = self.compute_amount(self.param_id.t851)
        self.t861 = self.compute_amount(self.param_id.t861)
        self.t921 = self.compute_amount(self.param_id.t921)
        self.t931 = self.compute_amount(self.param_id.t931)








