# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class G50Var(models.Model):
    _name = 'account.g50.var'

    name = fields.Char('Var')


class G50Jrn(models.Model):
    _name = 'account.g50.jrn'

    name = fields.Char('Journal')


class G50Param(models.Model):
    _name = 'account.g50.param'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tableau du parametrage G50'

    name    = fields.Char('Designation')
    state   = fields.Selection([('draft', 'Brouillon'), ('done', u'Validé')], string='Etat', default='draft')
    line_ids = fields.One2many('account.g50.param.line', 'g50param_id', string='Lignes')

    @api.multi
    def action_import(self):
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('l10n_dz_reports_g50', 'g50_import_params_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Importation parametrage G50',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'g50.import.params.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id},
            'target': 'new',
        }

    @api.multi
    def unlink(self):
        if self.state == 'done':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le document est validé ! \n\n Remettez en brouillon pour pouvoir supprimer'))
        else:
            self.line_ids.unlink()

            rec = super(G50Param, self).unlink()
            return rec

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_creation(self):
        self.line_ids.unlink()
        self.env['account.g50.param.line'].create({'name': 'c1a11_brut', 'g50param_id': self.id, 'sequence': 1, 'tableau': '1', 'ligne': 1, 'col': '1', 'code': 'C1A11_1', 'designation': 'Affaires bénéficiant d une réfaction de 50 % ', })
        self.env['account.g50.param.line'].create({'name': 'c1a12_brut', 'g50param_id': self.id, 'sequence': 2, 'tableau': '1', 'ligne': 2, 'col': '1', 'code': 'C1A12_1', 'designation': 'Affaires bénéficiant d une réfaction de 30 % ', })
        self.env['account.g50.param.line'].create({'name': 'c1a13_brut', 'g50param_id': self.id, 'sequence': 3, 'tableau': '1', 'ligne': 3, 'col': '1', 'code': 'C1A13_1', 'designation': 'Affaires sans réfaction', })
        self.env['account.g50.param.line'].create({'name': 'c1a14_brut', 'g50param_id': self.id, 'sequence': 4, 'tableau': '1', 'ligne': 4, 'col': '1', 'code': 'C1A14_1', 'designation': 'Affaires exonérées', })
        self.env['account.g50.param.line'].create({'name': 'c1a20_brut', 'g50param_id': self.id, 'sequence': 5, 'tableau': '1', 'ligne': 5, 'col': '1', 'code': 'C1A20_1', 'designation': 'Recettes professionnelles (Professions libérales)', })
        self.env['account.g50.param.line'].create({'name': 'c1a20_imp', 'g50param_id': self.id, 'sequence': 6, 'tableau': '1', 'ligne': 5, 'col': '2', 'code': 'C1A20_2', 'designation': 'Recettes professionnelles (Professions libérales)', })
        self.env['account.g50.param.line'].create({'name': 't212', 'g50param_id': self.id, 'sequence': 7, 'tableau': '2', 'ligne': 1, 'col': '2', 'code': 'E1M10_2', 'designation': 'Détermination des acomptes provisionnels', })
        self.env['account.g50.param.line'].create({'name': 't213', 'g50param_id': self.id, 'sequence': 8, 'tableau': '2', 'ligne': 1, 'col': '3', 'code': 'E1M10_3', 'designation': 'Acomptes IBS (Montant à payer)', })
        self.env['account.g50.param.line'].create({'name': 'e1l20_imp', 'g50param_id': self.id, 'sequence': 9, 'tableau': '3', 'ligne': 1, 'col': '1', 'code': 'E1L20_1', 'designation': 'IRG/ Traitements salaires, pensions et rentes viagères', })
        self.env['account.g50.param.line'].create({'name': 'e1l20_retenu', 'g50param_id': self.id, 'sequence': 10, 'tableau': '3', 'ligne': 1, 'col': '3', 'code': 'E1L20_3', 'designation': 'IRG/ Traitements salaires, pensions et rentes viagères', })
        self.env['account.g50.param.line'].create({'name': 'e1l30_imp', 'g50param_id': self.id, 'sequence': 11, 'tableau': '3', 'ligne': 2, 'col': '1', 'code': 'E1L30_1', 'designation': 'IRG/ Revenus des créances, dépôts et cautionnements', })
        self.env['account.g50.param.line'].create({'name': 'e1l40_imp', 'g50param_id': self.id, 'sequence': 12, 'tableau': '3', 'ligne': 3, 'col': '1', 'code': 'E1L40_1', 'designation': 'IRG/ Bénéfices distribués par les sociétés de capitaux, libératoire', })
        self.env['account.g50.param.line'].create({'name': 'e1l60_imp', 'g50param_id': self.id, 'sequence': 13, 'tableau': '3', 'ligne': 4, 'col': '1', 'code': 'E1L60_1', 'designation': 'IRG/ Revenus des bons de caisse anonymes', })
        self.env['account.g50.param.line'].create({'name': 'e1l80_imp', 'g50param_id': self.id, 'sequence': 14, 'tableau': '3', 'ligne': 5, 'col': '1', 'code': 'E1L80_1', 'designation': 'IRG/ Autres retenues à la source', })
        self.env['account.g50.param.line'].create({'name': 'e1l80_taux', 'g50param_id': self.id, 'sequence': 15, 'tableau': '3', 'ligne': 5, 'col': '2', 'code': 'E1L80_2', 'designation': 'IRG/ Autres retenues à la source', })
        self.env['account.g50.param.line'].create({'name': 'e1m30_imp', 'g50param_id': self.id, 'sequence': 16, 'tableau': '3', 'ligne': 6, 'col': '1', 'code': 'E1M30_1', 'designation': 'IBS/ Revenus des entreprises étrangères non installées en Algérie (prestations de services) (1)', })
        self.env['account.g50.param.line'].create({'name': 'e1m40_imp', 'g50param_id': self.id, 'sequence': 17, 'tableau': '3', 'ligne': 7, 'col': '1', 'code': 'E1M40_1', 'designation': 'IBS/ Autres retenues à la source ', })
        self.env['account.g50.param.line'].create({'name': 'e1m40_taux', 'g50param_id': self.id, 'sequence': 18, 'tableau': '3', 'ligne': 7, 'col': '2', 'code': 'E1M40_2', 'designation': 'IBS/ Autres retenues à la source ', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_1_libelle', 'g50param_id': self.id, 'sequence': 19, 'tableau': '4', 'ligne': 1, 'col': '1', 'code': 'E2E00_11', 'designation': 'Opérations imposables ', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_1_imp', 'g50param_id': self.id, 'sequence': 20, 'tableau': '4', 'ligne': 1, 'col': '2', 'code': 'E2E00_12', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_1_taux', 'g50param_id': self.id, 'sequence': 21, 'tableau': '4', 'ligne': 1, 'col': '3', 'code': 'E2E00_13', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_2_libelle', 'g50param_id': self.id, 'sequence': 22, 'tableau': '4', 'ligne': 2, 'col': '1', 'code': 'E2E00_21', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_2_imp', 'g50param_id': self.id, 'sequence': 23, 'tableau': '4', 'ligne': 2, 'col': '2', 'code': 'E2E00_22', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_2_taux', 'g50param_id': self.id, 'sequence': 24, 'tableau': '4', 'ligne': 2, 'col': '3', 'code': 'E2E00_23', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_3_libelle', 'g50param_id': self.id, 'sequence': 25, 'tableau': '4', 'ligne': 3, 'col': '1', 'code': 'E2E00_31', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_3_imp', 'g50param_id': self.id, 'sequence': 26, 'tableau': '4', 'ligne': 3, 'col': '2', 'code': 'E2E00_32', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 'e2e00_3_taux', 'g50param_id': self.id, 'sequence': 27, 'tableau': '4', 'ligne': 3, 'col': '3', 'code': 'E2E00_33', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't511', 'g50param_id': self.id, 'sequence': 28, 'tableau': '5', 'ligne': 1, 'col': '1', 'code': 'E2E05_11', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't512', 'g50param_id': self.id, 'sequence': 29, 'tableau': '5', 'ligne': 1, 'col': '2', 'code': 'E2E05_12', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't513', 'g50param_id': self.id, 'sequence': 30, 'tableau': '5', 'ligne': 1, 'col': '3', 'code': 'E2E05_13', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't521', 'g50param_id': self.id, 'sequence': 31, 'tableau': '5', 'ligne': 2, 'col': '1', 'code': 'E2E05_21', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't522', 'g50param_id': self.id, 'sequence': 32, 'tableau': '5', 'ligne': 2, 'col': '2', 'code': 'E2E05_22', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't523', 'g50param_id': self.id, 'sequence': 33, 'tableau': '5', 'ligne': 2, 'col': '3', 'code': 'E2E05_23', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't531', 'g50param_id': self.id, 'sequence': 34, 'tableau': '5', 'ligne': 3, 'col': '1', 'code': 'E2E05_31', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't532', 'g50param_id': self.id, 'sequence': 35, 'tableau': '5', 'ligne': 3, 'col': '2', 'code': 'E2E05_32', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't533', 'g50param_id': self.id, 'sequence': 36, 'tableau': '5', 'ligne': 3, 'col': '3', 'code': 'E2E05_33', 'designation': '', })
        self.env['account.g50.param.line'].create({'name': 't661', 'g50param_id': self.id, 'sequence': 37, 'tableau': '6', 'ligne': 6, 'col': '1', 'code': 'C/201 003/303/A/B', 'designation': '– TIC', })
        self.env['account.g50.param.line'].create({'name': 't711', 'g50param_id': self.id, 'sequence': 38, 'tableau': '7', 'ligne': 1,'col': '1', 'code': 'E3B11_1', 'designation': 'Biens, produits et denrées visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't712', 'g50param_id': self.id, 'sequence': 39, 'tableau': '7', 'ligne': 1,'col': '2', 'code': 'E3B11_2', 'designation': 'Biens, produits et denrées visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't721', 'g50param_id': self.id, 'sequence': 40, 'tableau': '7', 'ligne': 2,'col': '1', 'code': 'E3B12_1', 'designation': 'Prestations de services visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't722', 'g50param_id': self.id, 'sequence': 41, 'tableau': '7', 'ligne': 2,'col': '2', 'code': 'E3B12_2', 'designation': 'Prestations de services visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't731', 'g50param_id': self.id, 'sequence': 42, 'tableau': '7', 'ligne': 3,'col': '1', 'code': 'E3B13_1', 'designation': 'Opérations immobilières visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't732', 'g50param_id': self.id, 'sequence': 43, 'tableau': '7', 'ligne': 3,'col': '2', 'code': 'E3B13_2', 'designation': 'Opérations immobilières visées par l article 23 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't741', 'g50param_id': self.id, 'sequence': 44, 'tableau': '7', 'ligne': 4,'col': '1', 'code': 'E3B14_1', 'designation': 'Actes médicaux', })
        self.env['account.g50.param.line'].create({'name': 't742', 'g50param_id': self.id, 'sequence': 45, 'tableau': '7', 'ligne': 4,'col': '2', 'code': 'E3B14_2', 'designation': 'Actes médicaux', })
        self.env['account.g50.param.line'].create({'name': 't751', 'g50param_id': self.id, 'sequence': 46, 'tableau': '7', 'ligne': 5,'col': '1', 'code': 'E3B15_1', 'designation': 'Commissionnaires et courtiers', })
        self.env['account.g50.param.line'].create({'name': 't752', 'g50param_id': self.id, 'sequence': 47, 'tableau': '7', 'ligne': 5,'col': '2', 'code': 'E3B15_2', 'designation': 'Commissionnaires et courtiers', })
        self.env['account.g50.param.line'].create({'name': 't761', 'g50param_id': self.id, 'sequence': 48, 'tableau': '7', 'ligne': 6,'col': '1', 'code': 'E3B16_1', 'designation': 'Fourniture d énergie', })
        self.env['account.g50.param.line'].create({'name': 't762', 'g50param_id': self.id, 'sequence': 49, 'tableau': '7', 'ligne': 6,'col': '2', 'code': 'E3B16_2', 'designation': 'Fourniture d énergie', })
        self.env['account.g50.param.line'].create({'name': 't771', 'g50param_id': self.id, 'sequence': 50, 'tableau': '7', 'ligne': 7,'col': '1', 'code': 'E3B21_1', 'designation': 'Productions : biens, produits et denrées visées par lart. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't772', 'g50param_id': self.id, 'sequence': 51, 'tableau': '7', 'ligne': 7,'col': '2', 'code': 'E3B21_2', 'designation': 'Productions : biens, produits et denrées visées par l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't781', 'g50param_id': self.id, 'sequence': 52, 'tableau': '7', 'ligne': 8,'col': '1', 'code': 'E3B22_1', 'designation': 'Revente en l état : biens, produits et denrées visées par l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't782', 'g50param_id': self.id, 'sequence': 53, 'tableau': '7', 'ligne': 8,'col': '2', 'code': 'E3B22_2', 'designation': 'Revente en l état : biens, produits et denrées visées par l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't791', 'g50param_id': self.id, 'sequence': 54, 'tableau': '7', 'ligne': 9,'col': '1', 'code': 'E3B23_1', 'designation': 'Travaux immobiliers autres que ceux soumis au taux de 7%', })
        self.env['account.g50.param.line'].create({'name': 't792', 'g50param_id': self.id, 'sequence': 55, 'tableau': '7', 'ligne': 9,'col': '2', 'code': 'E3B23_2', 'designation': 'Travaux immobiliers autres que ceux soumis au taux de 7%', })
        self.env['account.g50.param.line'].create({'name': 't7a1', 'g50param_id': self.id, 'sequence': 56, 'tableau': '7', 'ligne': 10,'col': '1', 'code': 'E3B24_1', 'designation': 'Professions libérales', })
        self.env['account.g50.param.line'].create({'name': 't7a2', 'g50param_id': self.id, 'sequence': 57, 'tableau': '7', 'ligne': 10,'col': '2', 'code': 'E3B24_2', 'designation': 'Professions libérales', })
        self.env['account.g50.param.line'].create({'name': 't7b1', 'g50param_id': self.id, 'sequence': 58, 'tableau': '7', 'ligne': 11,'col': '1', 'code': 'E3B25_1', 'designation': 'Opérations de banques et d assurances', })
        self.env['account.g50.param.line'].create({'name': 't7b2', 'g50param_id': self.id, 'sequence': 59, 'tableau': '7', 'ligne': 11,'col': '2', 'code': 'E3B25_2', 'designation': 'Opérations de banques et d ssurances', })
        self.env['account.g50.param.line'].create({'name': 't7c1', 'g50param_id': self.id, 'sequence': 60, 'tableau': '7', 'ligne': 12,'col': '1', 'code': 'E3B26_1', 'designation': 'Prestations de téléphones et de télex', })
        self.env['account.g50.param.line'].create({'name': 't7c2', 'g50param_id': self.id, 'sequence': 61, 'tableau': '7', 'ligne': 12,'col': '2', 'code': 'E3B26_2', 'designation': 'Prestations de téléphones et de télex', })
        self.env['account.g50.param.line'].create({'name': 't7d1', 'g50param_id': self.id, 'sequence': 62, 'tableau': '7', 'ligne': 13,'col': '1', 'code': 'E3B28_1', 'designation': 'Autres prestations de services', })
        self.env['account.g50.param.line'].create({'name': 't7d2', 'g50param_id': self.id, 'sequence': 63, 'tableau': '7', 'ligne': 13,'col': '2', 'code': 'E3B28_2', 'designation': 'Autres prestations de services', })
        self.env['account.g50.param.line'].create({'name': 't7e1', 'g50param_id': self.id, 'sequence': 64, 'tableau': '7', 'ligne': 14,'col': '1', 'code': 'E3B31_1', 'designation': 'Débits de boissons', })
        self.env['account.g50.param.line'].create({'name': 't7e2', 'g50param_id': self.id, 'sequence': 65, 'tableau': '7', 'ligne': 14,'col': '2', 'code': 'E3B31_2', 'designation': 'Débits de boissons', })
        self.env['account.g50.param.line'].create({'name': 't7f1', 'g50param_id': self.id, 'sequence': 66, 'tableau': '7', 'ligne': 15,'col': '1', 'code': 'E3B32_1', 'designation': 'Productions : biens, produits et denrées visées par l article 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7f2', 'g50param_id': self.id, 'sequence': 67, 'tableau': '7', 'ligne': 15,'col': '2', 'code': 'E3B32_2', 'designation': 'Productions : biens, produits et denrées visées par l article 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7g1', 'g50param_id': self.id, 'sequence': 68, 'tableau': '7', 'ligne': 16,'col': '1', 'code': 'E3B33_1', 'designation': 'Revente en l état : biens, produits et denrées visées par l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7g2', 'g50param_id': self.id, 'sequence': 69, 'tableau': '7', 'ligne': 16,'col': '2', 'code': 'E3B33_2', 'designation': 'Revente en l état : biens, produits et denrées visées par l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7h1', 'g50param_id': self.id, 'sequence': 70, 'tableau': '7', 'ligne': 17,'col': '1', 'code': 'E3B34_1', 'designation': 'Tabacs et allumettes', })
        self.env['account.g50.param.line'].create({'name': 't7h2', 'g50param_id': self.id, 'sequence': 71, 'tableau': '7', 'ligne': 17,'col': '2', 'code': 'E3B34_2', 'designation': 'Tabacs et allumettes', })
        self.env['account.g50.param.line'].create({'name': 't7i1', 'g50param_id': self.id, 'sequence': 72, 'tableau': '7', 'ligne': 18,'col': '1', 'code': 'E3B35_1', 'designation': 'Spectacles, jeux et divertissements autres que ceux de l art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7i2', 'g50param_id': self.id, 'sequence': 73, 'tableau': '7', 'ligne': 18,'col': '2', 'code': 'E3B35_2', 'designation': 'Spectacles, jeux et divertissements autres que ceux de  art. 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7j1', 'g50param_id': self.id, 'sequence': 74, 'tableau': '7', 'ligne': 19,'col': '1', 'code': 'E3B36_1', 'designation': 'Autres prestations de services visées à l article 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7j2', 'g50param_id': self.id, 'sequence': 75, 'tableau': '7', 'ligne': 19,'col': '2', 'code': 'E3B36_2', 'designation': 'Autres prestations de services visées à l article 21 du C. TCA', })
        self.env['account.g50.param.line'].create({'name': 't7k1', 'g50param_id': self.id, 'sequence': 76, 'tableau': '7', 'ligne': 20,'col': '1', 'code': 'E3B37_1', 'designation': 'Consommations sur place ', })
        self.env['account.g50.param.line'].create({'name': 't7k2', 'g50param_id': self.id, 'sequence': 77, 'tableau': '7', 'ligne': 20,'col': '2', 'code': 'E3B37_2', 'designation': 'Consommations sur place ', })
        self.env['account.g50.param.line'].create({'name': 't811', 'g50param_id': self.id, 'sequence': 78, 'tableau': '8', 'ligne': 1,'col': '1', 'code': 'E3B91', 'designation': 'Précompte antérieurs (mois précédent) ', })
        self.env['account.g50.param.line'].create({'name': 't821', 'g50param_id': self.id, 'sequence': 79, 'tableau': '8', 'ligne': 2,'col': '1', 'code': 'E3B92', 'designation': 'TVA sur achats de biens, matières et services (art. 29 C. TCA)', })
        self.env['account.g50.param.line'].create({'name': 't831', 'g50param_id': self.id, 'sequence': 80, 'tableau': '8', 'ligne': 3,'col': '1', 'code': 'E3B91', 'designation': 'TVA sur achats de biens amortissables (art. 38 C. TCA)', })
        self.env['account.g50.param.line'].create({'name': 't841', 'g50param_id': self.id, 'sequence': 81, 'tableau': '8', 'ligne': 4,'col': '1', 'code': 'E3B92', 'designation': 'Régularisation du prorata (déduction complémentaire) (art. 40 C. TCA)', })
        self.env['account.g50.param.line'].create({'name': 't851', 'g50param_id': self.id, 'sequence': 82, 'tableau': '8', 'ligne': 5,'col': '1', 'code': 'E3B91', 'designation': 'TVA à récupérer sur factures annulées ou impayées (art. 18 C. TCA)', })
        self.env['account.g50.param.line'].create({'name': 't861', 'g50param_id': self.id, 'sequence': 83, 'tableau': '8', 'ligne': 6,'col': '1', 'code': 'E3B92', 'designation': 'Autres déductions (notification de précompte, etc.…)', })
        self.env['account.g50.param.line'].create({'name': 't921', 'g50param_id': self.id, 'sequence': 84, 'tableau': '9', 'ligne': 2,'col': '1', 'code': 'E3B97', 'designation': 'Régularisation du prorata (art. 40 C. TCA) (+) (déduction excédentaire)', })
        self.env['account.g50.param.line'].create({'name': 't931', 'g50param_id': self.id, 'sequence': 85, 'tableau': '9', 'ligne': 3,'col': '1', 'code': 'E3B98', 'designation': '- Reversement de la déduction (art. 38 C. TCA) (+)', })


class G50ParamLine(models.Model):
    _name = 'account.g50.param.line'
    _description = 'Ligne tableau du parametrage G50'
    _order = 'sequence'

    name        = fields.Char('Variable', readonly=1)
    sequence    = fields.Integer('Sequence', readonly=1)
    tableau     = fields.Selection([('1', 'tab1'), ('2', 'tab2'), ('3', 'tab3'), ('4', 'tab4'), ('5', 'tab5'),
                                    ('6', 'tab6'), ('7', 'tab7'), ('8', 'tab8'), ('9', 'tab9')], string='Tableau', readonly=1)
    ligne       = fields.Integer('Ligne', readonly=1)
    col         = fields.Selection([('1', '1'), ('2', '2'),
                                    ('3', '3'), ('4', '4')], string='Colonne', readonly=1)
    code        = fields.Char('Code')
    designation = fields.Char('Rubrique')
    # journal_ids = fields.Many2many('account.g50.jrn', string='Journaux')
    # formula     = fields.Many2many('account.g50.var', string='Formule')
    value       = fields.Char('Valeur')
    type_value  = fields.Selection([('int', 'Entier'), ('float', 'Réel'), ('str', 'Chaine de caracteres')], string='Type')
    journal_ch = fields.Char('Journaux')
    formula_ch  = fields.Char('Formule')
    arrondi     = fields.Boolean('Arrondi')
    g50param_id = fields.Many2one('account.g50.param', string='G50 Parametrage')
