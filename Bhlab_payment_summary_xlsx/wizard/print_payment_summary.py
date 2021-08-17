from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf
import datetime



class PrintPaymentSummary(models.TransientModel):
    _name = "print.payment.summary"
    
    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date
    
    from_date = fields.Date(string='From Date', default=_get_from_date)
    to_date = fields.Date(string='To Date', default=fields.Date.context_today)
    payment_summary_file = fields.Binary('Details de paiements')
    file_name = fields.Char('File Name')
    payment_report_printed = fields.Boolean('Detail des paiements')
    currency_id = fields.Many2one('res.currency','Currency', default=lambda self: self.env.user.company_id.currency_id)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, help='Select Partner for movement')
    xls_file = 'D:\\0001-Projects\\Dev_bhlab_odoo_12\\bhlab_addons\\Bhlab_payment_summary_xlsx_template\\templates\\payment_template.xlsx'

    @api.multi
    def action_print_payment_summary(self):

        INDEX = 15
        workbook = xlwt.Workbook()

        column_heading_style = easyxf('font:height 250;font:bold True;')
        column_heading_style_2 = easyxf('font:height 300;font:bold True;')
        column_heading_style_3 = easyxf('font:height 300; align: horiz center;pattern:'
                                        ' pattern solid, fore_color black; font: color white;'
                                        ' font:bold True;' "borders: top thin,bottom thin,left thin,right thin")
        total_style = easyxf('font:height 200; align: vert center; align: horiz center;pattern:' \
                          ' pattern solid, fore_color white; font: color red;' \
                          ' font:bold True;' "borders: top thin,bottom thin,left thin,right thin")
        total_style.num_format_str = '#,##0.00 [$DZD]'


        currency_style = easyxf('font:bold True; borders: top thin,bottom thin,left thin,right thin')
        currency_style.num_format_str = '#,##0.00 [$DZD]'
        border_style = easyxf('borders: top thin,bottom thin,left thin,right thin')

        worksheet = workbook.add_sheet('Details de paiements')

        worksheet.write(INDEX, 0, _('De'), column_heading_style)
        worksheet.write(INDEX, 2, _('A'), column_heading_style)
        worksheet.write(INDEX - 1, 0, _('Client'), column_heading_style_2)

        worksheet.write(INDEX + 2, 0, _('N'), column_heading_style_3)
        worksheet.write(INDEX + 2, 1, _('Date'), column_heading_style_3)

        worksheet.write(INDEX + 2, 2, _('Montant HT'), column_heading_style_3)
        worksheet.write(INDEX + 2, 3, _('Montant TVA'), column_heading_style_3)
        worksheet.write(INDEX + 2, 4, _('Montant TTC'), column_heading_style_3)

        worksheet.write(INDEX + 2, 5, _('Reste a payer'), column_heading_style_3)
        worksheet.write(INDEX + 2, 6, _('Date'), column_heading_style_3)
        worksheet.write(INDEX + 2, 7, _('Paiement'), column_heading_style_3)
        worksheet.write(INDEX + 2, 8, _('Memo'), column_heading_style_3)

        worksheet.col(0).width = 3000
        worksheet.col(1).width = 3000
        worksheet.col(2).width = 7000
        worksheet.col(3).width = 7000
        worksheet.col(4).width = 7000
        worksheet.col(5).width = 7000
        worksheet.col(6).width = 3000
        worksheet.col(7).width = 7000
        worksheet.col(8).width = 8000


        
        company = 'SARL BH Lab'
        slogan = 'EQUIPEMENTS ET RÉACTIFS DE LABORATOIRES.'
        adress = '130, Cité Cadat Rouiba, Alger 16012, Algérie'
        worksheet.write_merge(0, 2, 0, 1, company, easyxf('font:height 400; align: vert center; align: horiz center;pattern:' \
                ' pattern solid, fore_color white; font: color black;' \
                ' font:bold True;' "borders: top thin,bottom thin,left thin,right thin"))
        worksheet.write_merge(3, 3, 0, 3, slogan, easyxf('font:height 200;'))
        worksheet.write_merge(4, 4, 0, 4, adress, easyxf('font:height 200;'))

        row = INDEX + 3
        for wizard in self:

            heading = 'Detail des paiements (' + str(wizard.currency_id.name) + ')'
            worksheet.write_merge(INDEX - 6, INDEX - 3, 1, 6, heading, easyxf('font:height 600; align: vert center; align: horiz center;pattern:' \
                          ' pattern solid, fore_color white; font: color black;' \
                          ' font:bold True;' "borders: top thin,bottom thin,left thin,right thin"))
            worksheet.write_merge(INDEX - 1, INDEX - 1, 1, 6, wizard.partner_id.name, easyxf('font:height 300; align: horiz center;pattern:' \
                ' pattern solid, fore_color white; font: color black;' \
                ' font:bold True;' "borders: top thin,bottom thin,left thin,right thin"))

            worksheet.write(INDEX, 1, wizard.from_date.strftime('%d-%m-%Y'))
            worksheet.write(INDEX, 3, wizard.to_date.strftime('%d-%m-%Y'))

            invoice_objs = self.env['account.invoice'].search([('date_invoice', '>=', wizard.from_date),
                                                               ('date_invoice', '<=', wizard.to_date)])

            total_amount = 0.0
            total_amount_taxed = 0.0
            total_amount_untaxed = 0.0
            total_payments = 0.0
            total_amount_du = 0.0
            
            for invoice in invoice_objs:
                if invoice.partner_id == wizard.partner_id:
                    worksheet.write(row, 0, invoice.number, border_style)
                    worksheet.write(row, 1, invoice.date_invoice.strftime('%d-%m-%Y'), currency_style)
                    worksheet.write(row, 4, invoice.amount_total, currency_style)
                    worksheet.write(row, 3, invoice.amount_tax, currency_style)
                    worksheet.write(row, 2, invoice.amount_untaxed, currency_style)


                    curent_row = row
                    total_payment = 0.0
                    for p in invoice.payment_move_line_ids:
                        worksheet.write(row, 8, p.payment_id.communication,border_style)
                        for a in p.matched_debit_ids:
                            if invoice.number in a.debit_move_id.display_name:
                                total_payment += a.amount
                                worksheet.write(row, 6, a.create_date.strftime('%d-%m-%Y'), border_style)
                                worksheet.write(row, 7, a.amount, currency_style)
                                row += 1
                    worksheet.write(curent_row, 5, invoice.amount_total - total_payment, currency_style)
                    row += 1

                    total_amount += invoice.amount_total
                    total_amount_taxed += invoice.amount_tax
                    total_amount_untaxed += invoice.amount_untaxed
                    total_payments += total_payment
                    total_amount_du += invoice.amount_total - total_payment

            worksheet.write_merge(row , row , 0, 1, 'TOTAUX', total_style)
            worksheet.write(row , 2, total_amount, total_style)
            worksheet.write(row , 3, total_amount_taxed, total_style)
            worksheet.write(row , 4, total_amount_untaxed, total_style)
            worksheet.write(row , 5, total_amount_du, total_style)
            worksheet.write(row , 7, total_payments, total_style)



            footing1 = 'Tél. : +21321855200  Courriel: secretariat.bhlab@bhinvest.net  Web: http://www.bhlab-algeria.com'
            footing2 = 'SARL BH LAB capital de 700.000.000 DA – AGR N° 242/2020 & N° 111/2012'
            footing3 = 'RC N° 07 B 0974701 – A.I.N 16420101614 – N.I.F – 000716097470140 – N.I.S 000716420033849'
            footing4 = 'SGA- RIB-1: 021 00035 113 0009208-55 RIB-2: 021 00004 1130000644-40, CCP SGA 391575'

            worksheet.write_merge(row + 5, row + 5, 0, 8, footing1, easyxf('font:height 200; align: horiz center;'))
            worksheet.write_merge(row + 6, row + 6, 0, 8, footing2, easyxf('font:height 200; align: horiz center;'))
            worksheet.write_merge(row + 7, row + 7, 0, 8, footing3, easyxf('font:height 200; align: horiz center;'))
            worksheet.write_merge(row + 8, row + 8, 0, 8, footing4, easyxf('font:height 200; align: horiz center;'))
            

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.payment_summary_file = excel_file
            wizard.file_name = 'Detail des paiements.xls'
            wizard.payment_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'print.payment.summary',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
