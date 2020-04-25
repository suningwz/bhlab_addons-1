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
    _name    = 'dl.account.report.report'
    _inherit = 'dl.account.report.report'

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

        worksheet.write('B2', 'DESIGNATION DE L\'ENTREPRISE : ' + self.company_id.name, bold)
        worksheet.write('B3', 'N D\'IDENTIFIANT : ' + self.num_identif, bold)
        worksheet.write(1, 2 + self.nbr_col, 'TABLEAU N : ' + self.tableau_num, bold_right)

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 45)
        worksheet.set_column('C:C', 6)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)

        # worksheet.merge_range('D' + str(ligne_x + 1) + ':A' + str(ligne_x + i - 1), media, bold)
        worksheet.write('D5', self.name, titre_bold)
        worksheet.write('D6', 'AU ' + str(self.date_fin))
        worksheet.write(5, 2 + self.nbr_col, 'U : ' + self.devise_id.name, bold_right)

        # titre des colonnes
        ligne_x = 7
        col_y = 3

        worksheet.write(ligne_x, 1, 'Rubrique', bold_colonne)
        worksheet.write(ligne_x, 2, 'Notes', bold_colonne)
        for col in self.model_id.column_ids:
            worksheet.write(ligne_x, col_y, col.name, bold_right_colonne)
            col_y += 1
        # Titre des lignes
        r = 1
        for row in self.model_id.row_ids:
            align  = _get_align(row.aligne)
            police = 12 + (row.police-1) * 2
            format_row = workbook.add_format({'bold': row.bold, 'align': align, 'font_size': police, 'border': 1})
            worksheet.write(ligne_x + r, 1, row.name, format_row)
            r += 1
        # valeur des lignes
        r = 1
        for row in self.grid_ids:
            police = 12 + (row.police - 1) * 2
            if row.view_data:
                format_row = workbook.add_format({'bold': row.bold, 'align': 'right', 'font_size': police, 'num_format': money_mask, 'border': 1})
            else:
                format_row = workbook.add_format({'font_size': police, 'num_format': money_mask, 'border': 1, 'font_color': '#FFFFFF' })
            format_row_note = workbook.add_format({'bold': row.bold, 'align': 'center', 'font_size': police, 'border': 1})

            worksheet.write(ligne_x + r, 2, row.note_liste, format_row_note)
            if self.nbr_col > 0:
                worksheet.write(ligne_x + r, 3, row.amount_1, format_row)
            if self.nbr_col > 1:
                worksheet.write(ligne_x + r, 4, row.amount_2, format_row)
            if self.nbr_col > 2:
                worksheet.write(ligne_x + r, 5, row.amount_3, format_row)
            if self.nbr_col > 3:
                worksheet.write(ligne_x + r, 6, row.amount_4, format_row)
            if self.nbr_col > 4:
                worksheet.write(ligne_x + r, 7, row.amount_5, format_row)
            if self.nbr_col > 5:
                worksheet.write(ligne_x + r, 8, row.amount_6, format_row)
            if self.nbr_col > 6:
                worksheet.write(ligne_x + r, 9, row.amount_7, format_row)
            if self.nbr_col > 7:
                worksheet.write(ligne_x + r, 10, row.amount_8, format_row)
            r += 1

        workbook.close()

        m = open('tmp/'+w_file_name, 'rb')
        self.env['ir.attachment'].create({
            'name'        : w_file_name,
            'datas'       : base64.b64encode(m.read()),
            'description' : 'files',
            'res_name'    : w_file_name,
            'res_model'   : 'dl.account.report.report',
            'res_id'      : self.id,
            'datas_fname' : w_file_name,
            }) 
