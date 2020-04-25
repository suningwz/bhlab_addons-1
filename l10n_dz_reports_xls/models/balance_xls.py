# -*- coding: utf-8 -*-

from odoo import models, api, _
import base64
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


def _get_align(a):
    if a == 'D':
        return 'right'
    else:
        if a == 'C':
            return 'center'
        else:
            return 'left'


class AccountReportReport(models.Model):
    _name    = 'dl.report.balance'
    _inherit = 'dl.report.balance'

    @api.one
    def action_export_excel(self):
        premiere_colonne = 13
        w_file_name = self.name+self.exercice+'.xlsx'
        # path folder
        # pth = self.env['ir.config_parameter'].get_param('excel_path')

        workbook = xlsxwriter.Workbook('tmp/'+w_file_name)
        worksheet = workbook.add_worksheet()

        # format 
        money_mask         = '#,##0.00'
        titre_bold         = workbook.add_format({'bold': True, 'valign': 'vcenter', 'font_size': 28})
        bold               = workbook.add_format({'bold': True})
        bold_colonne       = workbook.add_format({'bg_color': '#C6C8CE', 'bold': True, 'border': 1})
        bold_right         = workbook.add_format({'bold': True, 'align': 'right'})
        bold_right_colonne = workbook.add_format({'bg_color': '#C6C8CE', 'bold': True, 'align': 'right', 'border': 1})
        bold_right_colonne_money = workbook.add_format({'bg_color': '#C6C8CE', 'num_format': money_mask, 'bold': True, 'align': 'right', 'border': 1})

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 45)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)

        # worksheet.merge_range('D' + str(ligne_x + 1) + ':A' + str(ligne_x + i - 1), media, bold)
        worksheet.write('D5', self.name, titre_bold)
        worksheet.write('D6', 'AU ' + str(self.date_fin))
        worksheet.write(5, 8, 'U : ' + self.devise_id.name, bold_right)

        # titre des colonnes
        ligne_x = 7

        worksheet.write(ligne_x, 1, 'Compte', bold_colonne)
        worksheet.write(ligne_x, 2, u'Libellé', bold_colonne)
        worksheet.write(ligne_x, 3, u'Débit initial', bold_right_colonne)
        worksheet.write(ligne_x, 4, u'Crédit initial', bold_right_colonne)
        worksheet.write(ligne_x, 5, u'Débit periode', bold_right_colonne)
        worksheet.write(ligne_x, 6, u'Crédit periode', bold_right_colonne)
        worksheet.write(ligne_x, 7, u'Solde débit', bold_right_colonne)
        worksheet.write(ligne_x, 8, u'Solde crédit', bold_right_colonne)
        # valeur des lignes
        r = 1
        format_row = workbook.add_format({'align': 'right', 'font_size': 12, 'num_format': money_mask, 'border': 1})
        format_row_note = workbook.add_format({'align': 'left', 'font_size': 12, 'border': 1})

        for row in self.line_ids:

            worksheet.write(ligne_x + r, 1, row.code, format_row_note)
            worksheet.write(ligne_x + r, 2, row.compte, format_row_note)
            worksheet.write(ligne_x + r, 3, row.init_debit, format_row)
            worksheet.write(ligne_x + r, 4, row.inti_credit, format_row)
            worksheet.write(ligne_x + r, 5, row.periode_debit, format_row)
            worksheet.write(ligne_x + r, 6, row.periode_credit, format_row)
            worksheet.write(ligne_x + r, 7, row.solde_debit, format_row)
            worksheet.write(ligne_x + r, 8, row.solde_credit, format_row)
            r += 1

        ligne_x += len(self.line_ids) + 1
        worksheet.write(ligne_x, 1, '', bold_right_colonne)
        worksheet.write(ligne_x, 2, 'Totaux', bold_right_colonne)
        worksheet.write(ligne_x, 3, self.init_debit, bold_right_colonne_money)
        worksheet.write(ligne_x, 4, self.inti_credit, bold_right_colonne_money)
        worksheet.write(ligne_x, 5, self.periode_debit, bold_right_colonne_money)
        worksheet.write(ligne_x, 6, self.periode_credit, bold_right_colonne_money)
        worksheet.write(ligne_x, 7, self.solde_debit, bold_right_colonne_money)
        worksheet.write(ligne_x, 8, self.solde_credit, bold_right_colonne_money)

        workbook.close()

        m = open('tmp/'+w_file_name, 'rb')
        self.env['ir.attachment'].create({
            'name'        : w_file_name,
            'datas'       : base64.b64encode(m.read()),
            'description' : 'files',
            'res_name'    : w_file_name,
            'res_model'   : 'dl.report.balance',
            'res_id'      : self.id,
            'datas_fname' : w_file_name,
            })
