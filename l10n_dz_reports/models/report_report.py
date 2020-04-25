# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import float_round


def premiere_lettre(ch):
    if ch[:1] == '-':
        return ch[1:2]
    else:
        return ch[:1]


class AccountReportReport(models.Model):
    _name    = 'dl.account.report.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order   = 'tableau_num'

    @api.one
    @api.depends('company_id')
    def _get_nif(self):
        if self.company_id and self.company_id.nif:
            lib = ''
            nif = self.company_id.nif
            for i in range(0, len(nif)):
                lib = lib + nif[i] + ' '
            self.num_identif = lib
        else:
            self.num_identif = u'**Saisisser le NIF sur la fiche Société**'

    @api.one
    @api.depends('input_ids')
    def _nbr_input(self):
        self.nbr_input = len(self.input_ids)

    name        = fields.Char('Titre', required=True, readonly=1, states={'draft': [('readonly', False)]}, translate=True, track_visibility='onchange')
    code        = fields.Char('Code', required=True, readonly=1, states={'draft': [('readonly', False)]})

    Entete      = fields.Char('Designation de l\'entreprise', translate=True)
    company_id  = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    num_identif = fields.Char(compute=_get_nif, string=u'Numéro d\'identification')
    pied        = fields.Char('Pied de page')
    balance_id  = fields.Many2one('dl.report.balance', string='Balance', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')

    date_debut  = fields.Date(related='balance_id.date_debut', string=u'Date début', readonly=1, store=True, track_visibility='onchange')
    date_fin    = fields.Date(related='balance_id.date_fin', string=u'Date fin', readonly=1, store=True, track_visibility='onchange')
    exercice    = fields.Char(related='balance_id.exercice', string='Exercice', size=4, readonly=1, store=True, track_visibility='onchange')
    devise_id   = fields.Many2one(related='balance_id.devise_id', string=u'Unité d\'affichage', readonly=1, store=True, track_visibility='onchange')

    grid_ids    = fields.One2many('account.report.report.grid', 'report_id', string='Lignes', copy=True, readonly=1, states={'draft': [('readonly', False)]})
    grid_ids_1  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_2  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_3  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_4  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_5  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_6  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_7  = fields.One2many(related='grid_ids', string='Lignes')
    grid_ids_8  = fields.One2many(related='grid_ids', string='Lignes')
    rep_specifique7_ids  = fields.One2many('account.report.specifique7', 'report_id', string='Lignes', readonly=1)
    rep_specifique12_ids = fields.One2many('account.report.specifique12', 'report_id', string='Lignes')
    input_ids   = fields.One2many('account.report.report.input', 'report_id', string='Montants saisis', copy=True, readonly=1, states={'draft': [('readonly', False)]})
    note_ids    = fields.One2many('account.report.report.grid.note', 'report_id', string='Notes', copy=True, readonly=1, track_visibility='onchange')
    state       = fields.Selection([('draft', 'Brouillon'), ('done', u'Terminé')], string='Etat', default='draft')

    model_id    = fields.Many2one('account.report.model', string='Modele', required=True, readonly=1, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    nbr_col     = fields.Integer(related='model_id.nbr_col', string='Nombre de colonne')
    mode_impression = fields.Selection(related='model_id.mode_impression', string='Orientation impression', readonly=1, states={'draft': [('readonly', False)]})
    report_name = fields.Char(related='model_id.report_name', string='Nom du rapport', readonly=1)
    groupe_id   = fields.Many2one(related='model_id.groupe_id', string='Groupe', readonly=1)
    groupe_name = fields.Char(related='model_id.groupe_id.name', string='Groupe', readonly=1)
    tableau_num = fields.Char(related='model_id.tableau_num', string='Tableau Numero', readonly=1, store=True)
    specifique  = fields.Boolean(related='model_id.specifique', string='Rapport spécifique', readonly=1, store=True)
    specifique_rep = fields.Selection(related='model_id.specifique_rep', string='Rapport spécifique', readonly=1, store=True)
    notes       = fields.Text('Notes' , translate=True)
    nbr_input   = fields.Integer(compute=_nbr_input, string='Nombre de valeurs saisie',  help=u'utilisé pour afficher ou pas longlet saisie')

    @api.multi
    def copy(self, default=None):
        default = default or {}
        default['name'] = self.name + ' (Copie)'
        return super(AccountReportReport, self).copy(default)

    # @api.onchange('balance_id')
    # def onchange_balance_id(self):
    #     if self.balance_id:
    #         self.date_debut = self.balance_id.date_debut
    #         self.date_fin   = self.balance_id.date_fin
    #         self.exercice   = self.balance_id.exercice
    #         self.devise_id   = self.balance_id.devise_id.id

    @api.multi
    def action_print(self):
        if self.report_name:
            return self.env.ref('l10n_dz_reports.'+self.report_name).report_action(self)
        else:
            if self.mode_impression == 'Paysage':
                return self.env.ref('l10n_dz_reports.action_print_report_doc_paysage').report_action(self)
            else:
                return self.env.ref('l10n_dz_reports.action_print_report_doc').report_action(self)

    @api.onchange('model_id', 'exercice')
    def onchange_date(self):
        if self.model_id:
            if not self.name:
                self.name = self.model_id.name
            if self.exercice:
                self.code = self.model_id.code + '-' + self.exercice
            else:
                self.code = self.model_id.code

        if self.exercice:
            if not self.date_debut:
                self.date_debut = self.exercice+'-01-01'
            if not self.date_fin:
                self.date_fin = self.exercice + '-12-31'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    def total_compte(self, compte, balance, debit_credit, operation=1):
        # debit et credit initial
        if balance != 0:
            req = "select sum(init_debit) as init_debit, sum(inti_credit) as init_credit, " \
                  "sum(periode_debit) as periode_debit, sum(periode_credit) as periode_credit, " \
                  "sum(solde_debit) as solde_debit, sum(solde_credit) as solde_credit " \
                  "from dl_report_balance_line " \
                  "where report_id = %s and (code like %s) "

            rub = (balance, compte+'%',)
            self._cr.execute(req, rub)
            res = self._cr.dictfetchall()

            init_debit     = 0.0
            init_credit    = 0.0
            periode_debit  = 0.0
            periode_credit = 0.0
            solde_debit    = 0.0
            solde_credit   = 0.0

            if res:
                if res[0].get('init_debit'):
                    init_debit = res[0].get('init_debit')
                if res[0].get('init_credit'):
                    init_credit = res[0].get('init_credit')
                if res[0].get('periode_debit'):
                    periode_debit = res[0].get('periode_debit')
                if res[0].get('periode_credit'):
                    periode_credit = res[0].get('periode_credit')
                if res[0].get('solde_debit'):
                    solde_debit = res[0].get('solde_debit')
                if res[0].get('solde_credit'):
                    solde_credit = res[0].get('solde_credit')

            periode = debit_credit[:1]
            d_c = debit_credit[1:]
            if periode == 'O':  # periode initiale
                if d_c == 'DB':
                    return operation * init_debit
                elif d_c == 'CR':
                    return operation * init_credit
                elif d_c == 'SD':
                    return operation * (init_debit - init_credit)
                elif d_c == 'SC':
                    return operation * (init_credit - init_debit)
                elif d_c == 'SX':
                    return operation * (abs(init_credit - init_debit))
                elif d_c == 'CZ':
                    if (init_credit - init_debit) > 0:
                        return operation * (init_credit - init_debit)
                    else:
                        return 0.0
                elif d_c == 'DZ':
                    if (init_debit - init_credit) > 0:
                        return operation * (init_debit - init_credit)
                    else:
                        return 0.0

            elif periode == 'P':
                if d_c == 'DB':
                    return operation * periode_debit
                elif d_c == 'CR':
                    return operation * periode_credit
                elif d_c == 'SD':
                    return operation * (periode_debit - periode_credit)
                elif d_c == 'SC':
                    return operation * (periode_credit - periode_debit)
                elif d_c == 'SX':
                    return operation * (abs(periode_credit - periode_debit))
                elif d_c == 'CZ':
                    if (periode_credit - periode_debit) > 0:
                        return operation * (periode_credit - periode_debit)
                    else:
                        return 0.0
                elif d_c == 'DZ':
                    if (periode_debit - periode_credit) > 0:
                        return operation * (periode_debit - periode_credit)
                    else:
                        return 0.0

            elif periode == 'S':
                if d_c == 'DB':
                    return operation * solde_debit
                elif d_c == 'CR':
                    return operation * solde_credit
                elif d_c == 'SD':
                    return operation * (solde_debit - solde_credit)
                elif d_c == 'SC':
                    return operation * (solde_credit - solde_debit)
                elif d_c == 'SX':
                    return operation * (abs(solde_credit - solde_debit))
                elif d_c == 'CZ':
                    if (solde_credit - solde_debit) > 0:
                        return operation * (solde_credit - solde_debit)
                    else:
                        return 0.0
                elif d_c == 'DZ':
                    if (solde_debit - solde_credit) > 0:
                        return operation * (solde_debit - solde_credit)
                    else:
                        return 0.0

            elif periode == 'V':
                if d_c == 'DB':
                    return operation * (init_debit + periode_debit)
                elif d_c == 'CR':
                    return operation * (init_credit + periode_credit)
                elif d_c == 'SD':
                    return operation * (init_debit  + periode_debit - init_credit - periode_credit)
                elif d_c == 'SC':
                    return operation * (init_credit + periode_credit - init_debit - periode_debit)
                elif d_c == 'SX':
                    return operation * (abs(init_credit + periode_credit - init_debit - periode_debit))
        else:
            return 0.0

    def calcul_elem(self, elem, periode):
        # Opérateur
        operateur = 1
        if elem[:1] == '-':
            operateur = -1
            elem = elem[1:]

        # utiliser quelle balance?
        balance = 0
        if self.balance_id:
            balance = self.balance_id.id
            if periode[-1:] != 'N':
                bl = self.balance_id
                for i in range(1, int(periode[-1:])+1):
                    if bl.parent_id:
                        bl = bl.parent_id
                        balance = bl.id
                    else:
                        balance = 0
                        # break

        # Calcul
        if elem[:1].isdigit():
            oper = 'SSX'
            compte = elem
        else:
            oper = elem[:3]
            compte = elem[3:]
        return self.total_compte(compte, balance, oper, operateur)

    def get_input(self, code):
        value = self.env['account.report.report.input'].search([('code', '=', code), ('report_id', '=', self.id)])
        if value.exists():
            return value[0].amount
        else:
            # message d'erreur
            return 0.0

    def get_cell(self, elem):
        operateur = 1
        if elem[:1] == '-':
            operateur = -1
            elem = elem[1:]

        tab_id = self.id
        row = elem[:-2]
        col = elem[-1:]

        # si le lien concerne un autre tableau
        if elem[:1] == 'L':
            row = elem[3:6]
            col = elem[-1:]
            tab_num = elem[1:3]
            tab = self.env['dl.account.report.report'].search([('groupe_id', '=', self.groupe_id.id),
                                                               ('balance_id', '=', self.balance_id.id),
                                                               ('tableau_num', '=', tab_num),
                                                               ])
            if tab.exists():
                tab_id = tab[0].id

        value = self.env['account.report.report.grid'].search([('code', '=', row), ('report_id', '=', tab_id)])
        if value.exists():
            if col == '1':
                return operateur * value.amount_1
            else:
                if col == '2':
                    return operateur * value.amount_2
                else:
                    if col == '3':
                        return operateur * value.amount_3
                    else:
                        if col == '4':
                            return operateur * value.amount_4
                        else:
                            if col == '5':
                                return operateur * value.amount_5
                            else:
                                if col == '6':
                                    return operateur * value.amount_6
                                else:
                                    if col == '7':
                                        return operateur * value.amount_7
                                    else:
                                        return operateur * value.amount_8
        else:
            return 0.0

    def compute_amount(self, row, col):
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

        formula = self.env['account.report.model.formula'].search([('name', '=', row+'C'+str(col)), ('report_id', '=', self.model_id.id)])
        if formula.exists():
            if formula.formula_ch:
                # récupération de la formule
                formule_str = formula.formula_ch
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
                        if premiere_lettre(var) in ('R', 'L'):
                            lst_mtn.append(self.get_cell(var))
                        elif premiere_lettre(var) == 'M':  # valeur saisie manuellement
                            lst_mtn.append(self.get_input(row + 'C' + str(col)))
                        else:  # calcul a partir des ecritures
                            lst_mtn.append(self.calcul_elem(var, formula.column_id.periode))
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
        else:
            return 0.0

    @api.one
    def grid_generate(self):
        i = 1
        for row in self.model_id.row_ids:
            # recuperer l'ordre de calcul
            ordre  = 1
            for c in range(1, 9):
                formula = self.env['account.report.model.formula'].search([('name', '=', row.code + 'C' + str(c)), ('report_id', '=', self.model_id.id)])
                if formula.exists():
                    ordre = formula[0].ordre

            self.env['account.report.report.grid'].create({
                'name'         : row.name,
                'code'         : row.code,  # + col.code,
                'ligne_num'    : i,
                'report_id'    : self.id,
                'report_row_id': row.id,
                'ordre'        : ordre,
            })
            i += 1
        self.grid_input()

    @api.one
    def grid_correction(self):
        for rec in self.grid_ids:
            rw_id = self.env['account.report.model.row'].search([('code', '=', rec.code), ('report_id', '=', self.model_id.id)])
            rec.report_row_id = rw_id.id

    @api.one
    def grid_input(self):
        j = 1
        for rec in self.model_id.formula_ids:
            if rec.formula_ch:
                formule_str = rec.formula_ch
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
                for frm in lst:
                    if premiere_lettre(frm) == 'M':
                        # créer si inexistant
                        cell = self.env['account.report.report.input'].search([('code', '=', rec.name), ('report_id', '=', self.id)])
                        if not cell.exists():
                            self.env['account.report.report.input'].create({
                                'name'  : j,
                                'row_id': rec.row_id.id,
                                'col_id': rec.column_id.id,
                                'code'  : rec.name,
                                'report_id': self.id,
                            })
                            j += 1

    def montant_arrandi(self, mtn):
        # if self.model_id.arrondir:
        #     return int(mtn)
        # else:
        return float_round(mtn, 2)

    @api.one
    def grid_compute_all(self):
        i = 1
        # for rec in sorted(self.grid_ids, key=itemgetter('ordre'), reverse=False):
        for rec in sorted(self.grid_ids, key=lambda line: line.ordre, reverse=False):
            print(rec.code + '  -  ' + rec.name)
            rec.amount_1 = self.montant_arrandi(self.compute_amount(rec.code, 1) / self.devise_id.division)
            rec.amount_2 = self.montant_arrandi(self.compute_amount(rec.code, 2) / self.devise_id.division)
            rec.amount_3 = self.montant_arrandi(self.compute_amount(rec.code, 3) / self.devise_id.division)
            rec.amount_4 = self.montant_arrandi(self.compute_amount(rec.code, 4) / self.devise_id.division)
            rec.amount_5 = self.montant_arrandi(self.compute_amount(rec.code, 5) / self.devise_id.division)
            rec.amount_6 = self.montant_arrandi(self.compute_amount(rec.code, 6) / self.devise_id.division)
            rec.amount_7 = self.montant_arrandi(self.compute_amount(rec.code, 7) / self.devise_id.division)
            rec.amount_8 = self.montant_arrandi(self.compute_amount(rec.code, 8) / self.devise_id.division)

    @api.one
    def grid_delete(self):
        self.grid_ids.unlink()
        # self.input_ids.unlink()
        # self.note_ids.unlink()

    @api.one
    def update_all(self):
        self.grid_delete()
        self.grid_generate()
        self.grid_compute_all()

    @api.one
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le rapport est validé ! \n\n Remettez en brouillon pour pouvoir supprimer'))
        else:
            self.grid_ids.unlink()
            self.input_ids.unlink()
            self.note_ids.unlink()
            rec = super(AccountReportReport, self).unlink()
            return rec

    def action_print_html(self):
        # return self.env.ref('l10n_dz_reports.action_print_report_web_doc').report_action(self)
        if self.report_name:
            return self.env.ref('l10n_dz_reports.' + self.report_name + '_html').report_action(self)
        else:
            return self.env.ref('l10n_dz_reports.action_print_report_web_doc').report_action(self)

    # specifique
    def update_specifique7(self):
        self.rep_specifique7_ids.unlink()
        # = fields.One2many('account.report.specifique7'
        immo = self.env['account.asset.asset'].search([('state', '=', 'close'),
                                                       ('cession', '=', True),
                                                       # ('date_cession', '&gt;', self.date_debut),
                                                       # ('date_cession', '&lt;', self.date_fin),
                                                       ])
        for rec in immo:
            self.env['account.report.specifique7'].create({
                'name': rec.name,
                'date_acquisition' : rec.date,
                'date_cession' : rec.cession_date,
                'amount_value': rec.value,
                'amount_amort': rec.valeur_ammortissement,
                'amount_net': rec.valeur_net,
                'amount_price': rec.cession_montant,
                'report_id': self.id,
            })


class AccountReportGrid(models.Model):
    _name        = 'account.report.report.grid'
    _order       = 'code'

    @api.one
    def _note_liste(self):
        if len(self.note_ids) > 0:
            note = ''
            for rec in self.note_ids:
                if note == '':
                    note = rec.name
                else:
                    note = note + ', ' + rec.name
            self.note_liste = note
        else:
            self.note_liste = ''

    name       = fields.Char('Rubrique', required=True, translate=True)
    code       = fields.Char('Code')
    ligne_num  = fields.Integer(u'Numéro ligne')
    note_ids   = fields.One2many('account.report.report.grid.note', 'row_id', string='Note')
    note_liste = fields.Char(compute=_note_liste, string='Notes')
    report_id  = fields.Many2one('dl.account.report.report', string='Rapport')
    report_row_id = fields.Many2one('account.report.model.row', string='Ligne du modele')
    police        = fields.Integer(related='report_row_id.police', string='Taille')
    aligne        = fields.Selection(related='report_row_id.aligne', string='aligne')
    bold          = fields.Boolean(related='report_row_id.bold', string='aligne')
    view_data     = fields.Boolean(related='report_row_id.view_data', string='Afficher les montants')
    amount_1   = fields.Float('Colonne 1')
    amount_2   = fields.Float('Colonne 2')
    amount_3   = fields.Float('Colonne 3')
    amount_4   = fields.Float('Colonne 4')
    amount_5   = fields.Float('Colonne 5')
    amount_6   = fields.Float('Colonne 6')
    amount_7   = fields.Float('Colonne 7')
    amount_8   = fields.Float('Colonne 8')
    ordre      = fields.Integer('Ordre')

    @api.multi
    def action_add_note(self):
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('l10n_dz_reports', 'add_note_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Nouvelle note',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'add.note.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': '1', 'default_line_id': self.id},
            'target': 'new',
        }

    @api.one
    def unlink(self):
        self.note_ids.unlink()
        rec = super(AccountReportGrid, self).unlink()
        return rec


class AccountReportGridNote(models.Model):
    _name   = 'account.report.report.grid.note'
    _order  = 'name'

    name    = fields.Char('Numero', required=True)
    date    = fields.Datetime('Date', default=datetime.now())
    note    = fields.Text('Note', translate=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    row_id  = fields.Many2one('account.report.report.grid', string='Ligne Rapport')
    code    = fields.Char(related='row_id.code', string='Code Rubrique')
    report_id = fields.Many2one(related='row_id.report_id', string='Rapport')


class AccountReportInput(models.Model):
    _name   = 'account.report.report.input'
    _order  = 'name'

    name    = fields.Integer('Numero', required=True)
    note    = fields.Char('Note')
    amount  = fields.Float('Montant')
    row_id  = fields.Many2one('account.report.model.row', string='Ligne')
    col_id  = fields.Many2one('account.report.model.column', string='Colonne')
    code    = fields.Char('Code Cellule')
    report_id = fields.Many2one('dl.account.report.report', string='Rapport')


class AccountReportSpecifique7(models.Model):
    _name   = 'account.report.specifique7'
    _description = '7/Tableau des immobilisations cédées'
    _order  = 'name'

    @api.depends('amount_net', 'amount_price')
    def _calcul_plus_moins_value(self):
        for rec in self:
            if rec.amount_price - rec.amount_net > 0:
                rec.plus_value  = rec.amount_price - rec.amount_net
                rec.moins_value = 0.0
            else:
                rec.moins_value = rec.amount_net - rec.amount_price
                rec.plus_value  = 0.0

    name             = fields.Char(u'Nature des Immobilisations cédées', required=True)
    date_acquisition = fields.Date('Date acquisition')
    date_cession     = fields.Date('Date cession')
    amount_value     = fields.Float(u'Montant net figurant à l\'actif')
    amount_amort     = fields.Float(u'Amortissements pratiqués')
    amount_net       = fields.Float(u'Valeur nette comptable')
    amount_price     = fields.Float(u'Prix de cession')
    plus_value       = fields.Float(compute=_calcul_plus_moins_value, string=u'Plus value')
    moins_value      = fields.Float(compute=_calcul_plus_moins_value, string=u'Moins value')
    report_id        = fields.Many2one('dl.account.report.report', string='Rapport')


class AccountReportSpecifique12(models.Model):
    _name   = 'account.report.specifique12'
    _description = u'12/ Commissions et courtages, redevances, honoraires, sous-traitance, rémunérations diverses et frais de siège'

    name      = fields.Char(u'Désignation des personnes bénéficiaires', required=True)
    num_if    = fields.Char(u'Numéro d\'identifiant fiscal')
    adresse   = fields.Char(u'Adresse')
    amount    = fields.Float(u'Montant perçu')
    report_id = fields.Many2one('dl.account.report.report', string='Rapport')
