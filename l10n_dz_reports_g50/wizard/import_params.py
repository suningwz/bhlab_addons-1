# -*- coding: utf-8 -*-

from odoo import models, fields, _
from datetime import datetime
from xlrd import open_workbook
from odoo.exceptions import UserError
from odoo.tools import float_compare
# import base64
from operator import itemgetter
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
    f.write(data.decode('base64'))
    # f.write(base64.b64decode(data)) - pour python 3, rajouter aussi import base64

    f.close()
    return file_path


def get_col_num(col_name):
    if col_name:
        return ord(col_name) - 65
    else:
        return -1


class G50ImportParamsWizard(models.TransientModel):
    _name = 'g50.import.params.wizard'

    name = fields.Many2one('account.g50.param', string=u'Document de paramétrage')
    w_file_name  = fields.Binary  ('Sélectionnez le document', required=True)
    filename     = fields.Char    ('Filename')
    print_report = fields.Boolean ('Afficher un rapport d\'erreur')
    error        = fields.Boolean ('Erreur')
    cntrl_only   = fields.Boolean ('Faire un controle seulement')

    def action_import(self):

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

        def _check_exist(sh, row, col, model, nfield, name_field, print_rep=False):
            field_val = str(sh.cell(row, col).value)
            if field_val:
                if field_val[-2:] == '.0':
                    field_val = field_val[:-2]
                # mat = self.env[model].search([(nfield, '=', field_val)])
                if not elem_exist_req(model, nfield, field_val):
                    self.error = True
                    msg = 'Erreur a la ligne ' + str(
                                row + 1) + ', Le ' + name_field + ' ['+ _supp_dot_0(field_val)+'] n\'existe pas sur la base Odoo, veuillez corriger sur le fichier excel ou créer cet élément puis relancer l\'importation'
                    if not print_rep:
                        raise UserError(_(msg))
                    else:
                        fid.write(str(row + 1) + ';' + name_field + ';' + _supp_dot_0(field_val) + '\n')
                        # fid.wl(str(row + 1) + ';' + name_field + ';' + _supp_dot_0(field_val))

        def verify_data(sh):
            for row in range(1, sh.nrows):
                _check_not_null(sh, row, MODEL_VAR, 'Nom de la variable')
                _check_not_null(sh, row, MODEL_TABLEAU, 'Numéro du tableau')
                _check_not_null(sh, row, MODEL_LIGNE, 'La ligne dans la tableau')
                _check_not_null(sh, row, MODEL_COL, 'La colonne dans la tableau')
                # _check_exist(sh, row, MODEL_JOURNAL, 'account_journal', 'code', 'Journal', self.print_report)
                # _check_exist(sh, row, MODEL_TIERS, 'res_partner', 'code_tiers', 'Tiers', self.print_report)
                # _check_not_null(sh, row, MODEL_COMPTE, 'Compte')
                # _check_exist(sh, row, MODEL_COMPTE, 'account_account', 'code', 'Compte', self.print_report)

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

        # début opération
        # parametre des numeros des colonnes
        MODEL_TABLEAU = 0
        MODEL_LIGNE   = 1
        MODEL_COL     = 2
        MODEL_VAR     = 3
        MODEL_CODE    = 4
        MODEL_LIB     = 5
        MODEL_JOUNRAL = 6
        MODEL_FORMULE = 7
        # MODEL_TYPE    = 8
        # MODEL_OPER    = 9

        # ouvrir excel
        book   = open_workbook(read_file(self.w_file_name))
        xsheet = book.sheet_by_index(0)

        # pour ecrire les erreurs d'importation sur un fichier csv
        if self.print_report:
            # fid = cfile('erreur_importation.csv', 'w')
            fid = open('erreur_importation.csv', 'w')
            # fid.wl('Ligne;Table;Valeur Non trouvé')
            fid.write('Ligne;Table;Valeur Non trouvé \n')

        # _logger.info("--------------------lancement------------------------------------- ")
        # verifier s'il n y a d'erreur ou de manque dans le fichier excel a importer

        self.error = False
        verify_data(xsheet)
        if self.print_report:
            fid.close()
        # _logger.info("--------------------verification-----ok------------------------------ ")

        # debut du traitmnt
        if self.error:
            if self.print_report:
                raise UserError(_('Fichier contient des anomalies, veuillez consulter le fichier log généré [erreur_importation.csv]'))
        else:
            if self.cntrl_only:
                raise UserError(_('Tout est OK'))

            for row_index in range(1, xsheet.nrows):
                self.env['account.g50.param.line'].create({
                    'name'    : _get_cell(xsheet, row_index, MODEL_VAR),
                    'tableau' : str(_get_cell(xsheet, row_index, MODEL_TABLEAU, True)),
                    'ligne'   : int(_get_cell(xsheet, row_index, MODEL_LIGNE, True)),
                    'col'     : str(_get_cell(xsheet, row_index, MODEL_COL, True)),
                    'code'    : _get_cell(xsheet, row_index, MODEL_CODE),
                    'designation' : _get_cell(xsheet, row_index, MODEL_LIB),
                    'journal_ch' : _get_cell(xsheet, row_index, MODEL_JOUNRAL),
                    'formula_ch' : _get_cell(xsheet, row_index, MODEL_FORMULE),
                    'g50param_id' : self.name.id,
                    # 'journal_ids' : _get_cell(xsheet, row_index, MODEL_JOUNRAL),
                    # 'formula' : _get_cell(xsheet, row_index, MODEL_FORMULE),
                    # 'type'    : _get_cell(xsheet, row_index, MODEL_TYPE),
                })
            return True
