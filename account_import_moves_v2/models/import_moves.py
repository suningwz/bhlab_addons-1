# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from xlrd import open_workbook
import xlrd
from odoo.exceptions import UserError
import base64
import logging
_logger = logging.getLogger(__name__)


# récuperer la valeur d'une cellule [row, col] sur la feuille excel sh
def _supp_dot_0(val):
    v = str(val)
    if len(v) > 2:
        if v[-2:] == '.0':
            v = v[:-2]
    return v


# récuperer la valeur d'une cellule [row, col] sur la feuille excel sh
def _get_cell(sh, row, col, st=False):
    if col == -1:
        return None
    else:
        value = sh.cell(row, col).value
        if st:
            value = str(value)
            if value[-2:] == '.0':
                value = value[:-2]
        return value


# vérifie si la valeur de la cellule est vide
def _check_not_null(sh, row, col, name_field):
    value = sh.cell(row, col).value
    if value and value != '':
        return True
    else:
        raise UserError(_(
            'Erreur a la ligne '+str(row+1)+', Le champs ('+name_field+') est vide, veuillez corriger sur le fichier excel et relancer l\'importation'))


def read_file(fname):
    # copier le fichier selectionné (Field.Binary) dans un fichier temporaire (avec un chemin connu) et utiliser le fichier tmp
    file_path = 'tmp/file.xlsx'
    data = fname
    f = open(file_path, 'wb')
    # f.write(data.decode('base64'))
    f.write(base64.b64decode(data))  # - pour python 3, rajouter aussi import base64

    f.close()
    return file_path


def read_file_csv(fname):
    # copier le fichier selectionné (Field.Binary) dans un fichier temporaire (avec un chemin connu) et utiliser le fichier tmp
    file_path = 'tmp/file.csv'
    data = fname
    f = open(file_path, 'wb')
    # f.write(data.decode('base64'))
    f.write(base64.b64decode(data))  # - pour python 3, rajouter aussi import base64

    f.close()
    return file_path


def get_col_num(col_name):
    if col_name:
        return ord(col_name) - 65
    else:
        return -1


def str_to_float(s_mtn):
    d = s_mtn
    if d:
        return float(d)
    else:
        return 0.0

# class cfile(file):
#     # subclass file to have a more convienient use of writeline
#     def __init__(self, name, mode = 'r'):
#         self = file.__init__(self, name, mode)
#
#     def wl(self, string):
#         self.writelines(string + '\n')
#         return None


class AccountImportMoves(models.Model):
    _name = 'account.import.moves'
    _description = 'Importation ecritures'

    @api.depends('pcs_ids', 'ecr_ids')
    def _totaux(self):
        for rec in self:
            self.nbr_piece = len(self.pcs_ids)
            self.nbr_ecriture = len(self.ecr_ids)
            self.debit = sum(line.debit for line in rec.ecr_ids)
            self.credit = sum(line.credit for line in rec.ecr_ids)

    @api.depends('err_ids')
    def _nbr_error(self):
        for rec in self:
            self.nbr_error = len(self.err_ids)

    name         = fields.Char    ('Numero opération', default='/', readonly=1)
    date         = fields.Date('Date', default=date.today(), readonly=1, states={'draft': [('readonly', False)], 'pret': [('readonly', False)]})
    w_file_name  = fields.Binary  ('Sélectionnez le document', required=True, readonly=1, states={'draft': [('readonly', False)]})
    filename     = fields.Char    ('Filename')
    fichier_imp  = fields.Char('Fichier importation', readonly=1)
    model2_id    = fields.Many2one('account.import.model', string='Modele d\'importation', required=True, readonly=1, states={'draft': [('readonly', False)]})
    # model_type   = fields.Selection(related='model2_id.type', string='Type fichier', readonly=1)
    # print_report = fields.Boolean ('Afficher un rapport d\'erreur')
    error        = fields.Boolean ('Erreur')
    # cntrl_only   = fields.Boolean ('Faire un controle seulement')
    currency_id  = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    pcs_ids      = fields.One2many('account.import.moves.piece', 'import_id', string='Pieces', readonly=1)
    ecr_ids      = fields.One2many('account.import.moves.ecriture', 'import_id', string='Ecritures', readonly=1)
    err_ids      = fields.One2many('account.import.moves.error', 'import_id', string='Erreurs', readonly=1)
    nbr_piece    = fields.Integer(compute=_totaux, string='Piéces')
    nbr_error    = fields.Integer(compute=_nbr_error, string='Nombre erreurs')
    nbr_ecriture = fields.Integer(compute=_totaux, string='Ecritures')
    debit        = fields.Monetary(compute=_totaux, string='Total débit')
    credit       = fields.Monetary(compute=_totaux, string='Total crédit')
    user_id      = fields.Many2one('res.users', string='Effectuée par ', default=lambda self: self.env.user, readonly=1, states={'draft': [('readonly', False)]})
    format_date  = fields.Char('Format date', default='%Y%m%d')
    state_piece  = fields.Selection([('draft', 'Brouillon'), ('posted', 'Validée')], required=True, string='Mettre les pieces dans l\'état', default='posted')
    journal_id   = fields.Many2one('account.journal', string=u'Journal réouverture', required=True)
    exercice_id  = fields.Many2one('account.exercice', string='Exercice', readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', u'Préparation'),
                              ('error', 'Erreur'),
                              ('pret', 'Pret'),
                              ('import', u'Importé'),
                              ('done', u'Validé'),
                              ('cancel', u'Annulé'),
                              ], string='Etat', default='draft')

# ok
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('account.import.moves') or '/'

        return super(models.Model, self).create(vals)

    def unlink(self):
        if self.state == 'done':
            raise UserError(_('Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))

        self.ecr_ids.unlink()
        self.pcs_ids.unlink()
        self.err_ids.unlink()
        return super(models.Model, self).unlink()

    def action_control(self):
        self.transforme_file()

        if self.verifier_data():
            self.state = 'pret'
        else:
            self.state = 'error'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'
        self.ecr_ids.unlink()
        self.pcs_ids.unlink()
        self.err_ids.unlink()
        self.filename = None
        # self.w_file_name = None

    def verifier_data(self):

        def elem_exist_req(model, nfield, value):
            req = "select count(*) as nbr from "+model+" where "+nfield+"=%s;"
            rub = (value,)
            self._cr.execute(req, rub)
            res = self._cr.dictfetchall()
            num = res[0].get('nbr')
            if not num or num == 0 :
                return False
            else:
                return True

        def _check_exist(sh, row, col, model, nfield, name_field):
            field_val = str(sh.cell(row, col).value)
            if field_val:
                if field_val[-2:] == '.0':
                    field_val = field_val[:-2]
                # mat = self.env[model].search([(nfield, '=', field_val)])
                if not elem_exist_req(model, nfield, field_val):
                    self.error = True
                    err = self.env['account.import.moves.error'].search([('import_id', '=', self.id),
                                                                         ('elem', '=', _supp_dot_0(field_val)),
                                                                         ('type', '=', name_field)])
                    if err.exists():
                        err.lines += str(row + 1) + ', '
                    else:
                        self.env['account.import.moves.error'].create({
                            'name': str(len(self.err_ids)+1),
                            'sequence': len(self.err_ids)+1,
                            'type': name_field,
                            'elem': _supp_dot_0(field_val),
                            'lines': str(row + 1) + ', ',
                            'import_id': self.id,
                        })

        def verify_data(sh):
            for row in range(1, sh.nrows):
                _check_not_null(sh, row, MODEL_NUMERO_PIECE, 'Numéro Piéce')
                _check_not_null(sh, row, MODEL_DATE, 'Date')
                _check_not_null(sh, row, MODEL_JOURNAL, 'Journal')
                _check_exist(sh, row, MODEL_JOURNAL, 'account_journal', 'code', 'Journal')
                _check_exist(sh, row, MODEL_TIERS, 'res_partner', 'code_tiers', 'Tiers')
                _check_not_null(sh, row, MODEL_COMPTE, 'Compte')
                _check_exist(sh, row, MODEL_COMPTE, 'account_account', 'code', 'Compte')

        # parametre des numeros des colonnes
        MODEL_NUMERO_PIECE = self.model2_id.col_name
        MODEL_JOURNAL      = self.model2_id.col_journal
        MODEL_DATE         = self.model2_id.col_date
        MODEL_TIERS        = self.model2_id.col_partner
        MODEL_COMPTE       = self.model2_id.col_account

        # ouvrir excel
        book = open_workbook(self.fichier_imp)
        xsheet = book.sheet_by_index(0)

        # verifier s'il n y a d'erreur ou de manque dans le fichier excel a importer
        self.error = False
        self.err_ids.unlink()
        verify_data(xsheet)
        # _logger.info("--------------------verification-----ok------------------------------ ")
        if self.error:
            return False
        else:
            return True

    def transforme_file(self):
        # if self.model_type == 'Excel':
        self.fichier_imp = read_file(self.w_file_name)
        # else:
        #     #  convertir le fichier texte vers excel
        #     read_file_csv(self.w_file_name)
        #
        #     # Read in the file
        #     with open('tmp/file.csv', 'r') as fle:
        #         filedata = fle.read()
        #
        #     # Replace the target string
        #     filedata = filedata.replace(';', ',')
        #
        #     # Write the file out again
        #     with open('tmp/file.csv', 'w') as fle:
        #         fle.write(filedata)
        #
        #     with open('tmp/file.csv', 'rb') as f:
        #         result = chardet.detect(f.read())
        #
        #     pd.read_csv('tmp/file.csv', encoding=result['encoding']).to_excel('tmp/pandas_simple2.xlsx')
        #     self.fichier_imp = 'tmp/pandas_simple2.xlsx'

    def action_importer(self):
        self.state = 'import'
        self.action_import_xls()

    def action_import_xls(self):
        def _delete_partner_link():  # piece):
            # les tiers null ne sont pas bien enregistrés dans les ecritures, la ou il y a None, on retrouve le code tiers de la piece
            # pour regler le probleme, lors de la création des ecritures, la ou il n'y a pas de tiers, on enregistre le tiers (1)
            # aprés enregistrement cette fonction est lancée pour remettre tout les tiers 1 a None

            req = "update account_import_moves_ecriture set partner_id=Null where partner_id=1"
            rub = ()
            self._cr.execute(req, rub)

        def _get_field_id(sh, row, col, model, nfield):
            if col == -1:  # la colonne n'existe pas sur excel
                return None
            else:
                field_val = str(sh.cell(row, col).value)
                if field_val:
                    if field_val[-2:] == '.0':
                        field_val = field_val[:-2]
                    mat = self.env[model].search([(nfield, '=', field_val)])
                    if mat.exists():
                        return mat[0].id
                    else:
                        return None
                else:  # la colonne existe mais elle n'est pas renseignée
                    return None

        def create_piece(sheet):  # , vjournal, vpiece):
            # recuperer la marque et la référence pour verifier si le produit existe ou pas
            journal_id  = _get_field_id(sheet, row_index, MODEL_JOURNAL, 'account.journal', 'code')
            numro_piece = _get_cell(sheet, row_index, MODEL_NUMERO_PIECE, True)

            piece = self.env['account.move'].search([('name', '=', numro_piece), ('journal_id', '=', journal_id)])
            if not piece.exists():
                # creation de la piece
                if self.journal_id.id == journal_id:  # journal ouverture
                    py_date = datetime(int(self.exercice_id.name), 1, 1)
                else:
                    try:
                        # if _get_cell(xsheet, row_index, MODEL_DATE, True).isdigit():
                        #     py_date  = datetime(*xlrd.xldate.xldate_as_tuple(int(_get_cell(xsheet, row_index, MODEL_DATE)), book.datemode))
                        # else:
                        d_txt = _get_cell(xsheet, row_index, MODEL_DATE)
                        date_time_obj = datetime.strptime(d_txt, self.format_date)

                        py_date = date_time_obj.date()
                    except:
                        raise UserError(_(
                            'Il y a un probleme de format de date, si la date de votre fichier excel est au format texte, veuillez'
                            'préciser son format.\n exemple : 2018-01-15 -> format = %Y-%m-%d'))

                prd_id = self.env['account.import.moves.piece'].create({
                    'name'        : str(_get_cell(sheet, row_index, MODEL_JOURNAL, True))+'/'+self.exercice_id.name+'/'+numro_piece,
                    'journal_id'  : journal_id,
                    'ref'         : '',
                    'date'        : py_date,
                    'partner_id'  : _get_field_id(sheet, row_index, MODEL_TIERS, 'res.partner', 'code_tiers'),
                    'import_id'   : self.id,
                })
                return prd_id
            else:
                return piece[0]

        def create_ecriture(sheet, piece):
            # recuperer la marque et la référence pour verifier si le produit existe ou pas

            debit = str_to_float(_get_cell(sheet, row_index, MODEL_DEBIT))
            credit = str_to_float(_get_cell(sheet, row_index, MODEL_CREDIT))

            account    = _get_field_id(sheet, row_index, MODEL_COMPTE, 'account.account', 'code')
            account_id = self.env['account.account'].browse(account)
            partner_id = _get_field_id(sheet, row_index, MODEL_TIERS, 'res.partner', 'code_tiers')

            try:
                # if _get_cell(xsheet, row_index, MODEL_DATE, True).isdigit():
                #     py_date = datetime(
                #         *xlrd.xldate.xldate_as_tuple(int(_get_cell(xsheet, row_index, MODEL_DATE)), book.datemode))
                # else:
                d_txt = _get_cell(xsheet, row_index, MODEL_DATE)
                date_time_obj = datetime.strptime(d_txt, self.format_date)

                py_date = date_time_obj.date()
            except:
                raise UserError(_(
                    'Il y a un probleme de format de date, si la date de votre fichier excel est au format texte, veuillez'
                    'préciser son format.\n exemple : 2018-01-15 -> format = %Y-%m-%d'))

            self.env['account.import.moves.ecriture'].create({
                'sequence'    : _get_cell(sheet, row_index, MODEL_SEQUENCE),
                'name'        : _get_cell(sheet, row_index, MODEL_LIBELLE),
                'journal_id'  : _get_field_id(sheet, row_index, MODEL_JOURNAL, 'account.journal', 'code'),
                'account_id'  : account,
                'debit'       : debit,
                'credit'      : credit,
                'move_id'     : piece.id,
                'ref'         : _get_cell(sheet, row_index, MODEL_REF, True),
                'date'        : py_date,
                'partner_id'  : partner_id or None,
                'user_type_id': account_id.user_type_id.id,
                'import_id'   : self.id,
                'piece_id'    : piece.id,
            })

        # début opération
        # parametre des numeros des colonnes
        MODEL_NUMERO_PIECE = self.model2_id.col_name
        MODEL_JOURNAL      = self.model2_id.col_journal
        MODEL_REF          = self.model2_id.col_ref
        MODEL_DATE         = self.model2_id.col_date
        MODEL_SEQUENCE     = self.model2_id.col_sequence
        MODEL_TIERS        = self.model2_id.col_partner
        MODEL_DEBIT        = self.model2_id.col_debit
        MODEL_CREDIT       = self.model2_id.col_credit
        MODEL_COMPTE       = self.model2_id.col_account
        MODEL_LIBELLE      = self.model2_id.col_libelle

        # ouvrir excel
        book   = open_workbook(self.fichier_imp)
        xsheet = book.sheet_by_index(0)

        # _logger.info("--------------------lancement------------------------------------- ")
        num_piece  = None
        journal    = None
        piece_id   = None
        _logger.info("---ligne------------------------------------- : debut ")
        for row_index in range(1, xsheet.nrows):
            _logger.info("---ligne------------------------------------- : %s ", row_index)
            p = _get_cell(xsheet, row_index, MODEL_NUMERO_PIECE, True)
            j = _get_cell(xsheet, row_index, MODEL_JOURNAL, True)
            if num_piece != p or journal != j :
                piece_id  = create_piece(xsheet)

                num_piece = p
                journal   = j

            create_ecriture(xsheet, piece_id)

            if row_index % 50 == 0:
                _logger.info("---ligne------------------------------------- : %s ", row_index)
        _logger.info("---ligne------------------------------------- : fin ")

        # _delete_partner_link()  # supprimer les tiers = 1

# en cours

    def action_done(self):
        def to_str(m):
            if m:
                return str(m)
            else:
                return ''

        def f_to_str(m):
            if m:
                return str(m)
            else:
                return '0'

        def id_to_str(m):
            if m:
                return str(m).replace("'", " ")
            else:
                return 'Null'
        cpt = 0
        for pcs in self.pcs_ids:
            cpt += 1
            _logger.info("---Importation piece ------------------------------------- : %s ", cpt)
            p = self.env['account.move'].create({
                'name'       : pcs.name,
                'journal_id' : pcs.journal_id.id,
                'ref'        : pcs.ref,
                'date'       : pcs.date,
                'currency_id': self.env.user.company_id.currency_id.id,
                'state'      : self.state_piece,
                'partner_id' : pcs.partner_id.id,
                'company_id' : self.env.user.company_id.id,
                'narration'  : '',
                'create_uid' : self.env.user.id,
                'create_date': datetime.now(),
                'write_uid'  : self.env.user.id,
                'write_date' : datetime.now(),
            })
            req = 'insert into account_move_line (name,journal_id,account_id,debit,credit,balance,' \
                  'debit_cash_basis,credit_cash_basis,balance_cash_basis,ref,date,date_maturity,partner_id,user_type_id,' \
                  'company_currency_id,company_id,quantity,blocked,reconciled,move_id) values \n'
            i = 0
            for ecr in pcs.ecr_ids:
                i += 1
                req += "('" + ecr.name.replace("'", " ") + "'," + str(ecr.journal_id.id) + "," + str(ecr.account_id.id) + ", "
                req += f_to_str(ecr.debit) + ", " + f_to_str(ecr.credit) + ", " + f_to_str(ecr.debit - ecr.credit) + ", " + f_to_str(ecr.debit) + ", " + f_to_str(ecr.credit)
                req += ", " + f_to_str(ecr.debit - ecr.credit) + ",'" + to_str(ecr.ref) + "', '" + to_str(ecr.date) + "', '" + to_str(ecr.date) + "', "
                req += id_to_str(ecr.partner_id.id) + ", " + str(ecr.account_id.user_type_id.id) + ", " + str(self.env.user.company_id.currency_id.id)
                if i == len(pcs.ecr_ids):
                    req += ", " + str(self.env.user.company_id.id) + ", 1, False, " + str(ecr.account_id.reconcile) + ", " + str(p.id) + "); \n"
                else:
                    req += ", " + str(self.env.user.company_id.id) + ", 1, False, " + str(ecr.account_id.reconcile) + ", " + str(p.id) + "), \n"

            _logger.info("%s", req)
            rub = ()
            self._cr.execute(req, rub)
            p.amount = pcs.amount

        self.state = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Pièces comptables importées avec succés',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }


class AccountImportMovesPiece(models.Model):
    _name = 'account.import.moves.piece'
    _description = u'Pièce importée'

    @api.depends('ecr_ids.debit')
    def _total_amount(self):
        for rec in self:
            rec.amount = sum(line.debit for line in rec.ecr_ids)

    name        = fields.Char('Numero', readonly=1)
    journal_id  = fields.Many2one('account.journal', string='Journal', readonly=1)
    ref         = fields.Char(u'Référence', readonly=1)
    date        = fields.Date('Date', readonly=1)
    currency_id = fields.Many2one(related='import_id.currency_id', readonly=1)
    partner_id  = fields.Many2one('res.partner', string='Tiers', readonly=1)
    amount      = fields.Monetary(compute=_total_amount, string='Montant', readonly=1)
    narration   = fields.Char('Narration', readonly=1)
    import_id   = fields.Many2one('account.import.moves', string='Opération', readonly=1)
    ecr_ids     = fields.One2many('account.import.moves.ecriture', 'piece_id', string='Ecritures', readonly=1)
    # not_import  = fields.Boolean('Ne pas importer')


class AccountImportMovesEcriture(models.Model):
    _name = 'account.import.moves.ecriture'
    _description = u'Ecriture importée'
    _order = 'journal_id,piece_id,name,debit,credit'

    name         = fields.Char('Numero')
    sequence     = fields.Integer('Sequence')
    journal_id   = fields.Many2one('account.journal', string='Journal')
    ref          = fields.Char(u'Référence')
    date         = fields.Date('Date')
    currency_id  = fields.Many2one(related='import_id.currency_id')
    partner_id   = fields.Many2one('res.partner', string='Tiers')
    debit        = fields.Monetary('Débit')
    credit       = fields.Monetary('Crédit')
    account_id   = fields.Many2one('account.account', string='Compte')
    piece_id     = fields.Many2one('account.import.moves.piece', string=u'Piéce')
    user_type_id = fields.Many2one('account.account.type', string='Type')
    import_id    = fields.Many2one('account.import.moves', string='Opération')


class AccountImportMovesError(models.Model):
    _name = 'account.import.moves.error'
    _description = u'Erreurs fichier importation'
    _order = 'sequence'

    name         = fields.Char('Numéro')
    sequence     = fields.Integer('#')
    type         = fields.Char('Type')
    elem         = fields.Char(u'Elément non trouvé')
    lines        = fields.Char(u'Lignes')
    import_id    = fields.Many2one('account.import.moves', string='Opération')
