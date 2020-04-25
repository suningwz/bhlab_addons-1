# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountReportModel(models.Model):
    _name    = 'account.report.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order   = 'tableau_num'

    @api.depends('column_ids')
    def _nbr_col(self):
        for rec in self:
            rec.nbr_col = len(rec.column_ids)

    name        = fields.Char('Titre', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange', translate=True)
    sous_titre  = fields.Char('Sous titre', readonly=1, states={'draft': [('readonly', False)]}, translate=True)
    code        = fields.Char('Code', required=True, readonly=1, states={'draft': [('readonly', False)]})
    tableau_num = fields.Char('Tableau Numero', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    # Entete      = fields.Char('Designation de l\'entreprise')
    num_identif = fields.Char(u'Numéro d\'identification')
    arrondir = fields.Boolean(u'Arrondir les montants', default=True)
    # pied        = fields.Char('Pied de page')
    groupe_id   = fields.Many2one('account.report.group', string='Groupe', readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    row_ids     = fields.One2many('account.report.model.row', 'report_id', string='Lignes', copy=True, readonly=1, states={'draft': [('readonly', False)]})
    column_ids  = fields.One2many('account.report.model.column', 'report_id', string='Colonnes', copy=True, readonly=1, states={'draft': [('readonly', False)]})
    formula_ids = fields.One2many('account.report.model.formula', 'report_id', string='Colonnes', copy=True, readonly=1, states={'draft': [('readonly', False)]})
    state       = fields.Selection([('draft', 'Brouillon'), ('done', u'Terminé')], string='Etat', default='draft', track_visibility='onchange')
    nbr_col     = fields.Integer(compute=_nbr_col, string='Nombre colonnes')
    mode_impression = fields.Selection([('Portrait', 'Portrait'), ('Paysage', 'Paysage')], string='Orientation Impression', default='Portrait', readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    report_name = fields.Char('Nom du rapport', readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    specifique = fields.Boolean(u'Rapport spécifique', required=True)
    specifique_rep = fields.Selection([('standard', 'Standard'),
                                       ('7_immo_cede', '7/Tableau des immobilisations cédées'),
                                       ('12_commission', '12/Commissions et courtages, redevances, ... '),
                                       ], required=True, default='standard')

    @api.multi
    def copy(self, default=None):
        default = default or {}

        default['name'] = self.name + ' (Copie)'
        return super(AccountReportModel, self).copy(default)

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def fomula_generate_grid(self):
        for row in self.row_ids:
            for col in self.column_ids:
                elem = self.env['account.report.model.formula'].search([('name', '=', row.code + col.code), ('report_id', '=', self.id)])
                if not elem.exists():
                    self.env['account.report.model.formula'].create({
                        'name'     : row.code + col.code,
                        'column_id': col.id,
                        'row_id'   : row.id,
                        'periode'  : col.periode,
                        'report_id': self.id,
                        # 'formula': None,
                        'ordre'    : row.ordre,
                    })

    @api.one
    def fomula_delete_all(self):
        self.formula_ids.unlink()

    @api.one
    def fomula_delete_rows(self):
        self.row_ids.unlink()

    @api.one
    def fomula_delete_columns(self):
        self.column_ids.unlink()

    # @api.one
    # def fomula_delete_blank(self):
    #     self.formula_ids.unlink()

    # def param_export_to_excel

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le modéle est validé ! \n\n Remettez en brouillon pour pouvoir supprimer'))
        else:
            self.formula_ids.unlink()
            self.row_ids.unlink()
            self.column_ids.unlink()

            rec = super(AccountReportModel, self).unlink()
            return rec


class AccountReportModelRow(models.Model):
    _name        = 'account.report.model.row'
    _order       = 'code'

    @api.model
    def _get_default_code(self):

        return 'R'+str(len(self.report_id.row_ids))

    name        = fields.Char('Rubrique', required=True, translate=True)
    code        = fields.Char('Code', required=True, default=lambda self: self._get_default_code())
    ligne_num   = fields.Integer(u'Numéro ligne')
    ordre       = fields.Integer('Ordre de calcul')
    report_id   = fields.Many2one('account.report.model', string='Rapport')
    bold        = fields.Boolean('Gras')
    police      = fields.Integer('Taille', default=1)
    aligne      = fields.Selection([('G', 'G'), ('C', 'C'), ('D', 'D'), ], string='Aligne', default='G')
    view_data   = fields.Boolean('Afficher les montants', default=True)


class AccountReportModelColumn(models.Model):
    _name        = 'account.report.model.column'
    _order       = 'c_num'

    name      = fields.Char('Titre', required=True, translate=True)
    code      = fields.Char('Code', required=True)
    c_num     = fields.Integer(u'Numéro colonne', required=True)
    periode   = fields.Selection([('N', 'N'), ('N-1', 'N-1'), ('N-2', 'N-2'), ], string='Periode', default='N')
    report_id = fields.Many2one('account.report.model', string='Rapport')


class AccountReportModelFormula(models.Model):
    _name        = 'account.report.model.formula'
    _order       = 'name'

    name       = fields.Char('Code', required=True)
    column_id  = fields.Many2one('account.report.model.column', string='Colonne', required=True)
    row_id     = fields.Many2one('account.report.model.row', string='Ligne', required=True)
    periode    = fields.Selection(related='column_id.periode', string='Periode', required=True)
    report_id  = fields.Many2one('account.report.model', string='Rapport', required=True)
    # formula    = fields.Many2many('account.report.var', string='Var')
    formula_ch = fields.Char('Formule')
    ordre      = fields.Integer('Ordre de calcul', required=True)

    @api.onchange('row_id')
    def onchange_row(self):
        if self.row_id:
            if self.column_id:
                self.name = self.row_id.code+self.column_id.code
            else:
                self.name = self.row_id.code

    @api.onchange('column_id')
    def onchange_column(self):
        if self.column_id:
            if self.row_id:
                self.name = self.row_id.code+self.column_id.code
            else:
                self.name = self.column_id.code
