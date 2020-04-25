# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import datetime


class AddNoteWizard(models.TransientModel):
    _name = 'add.note.wizard'

    name    = fields.Char('operation', required=True)
    line_id = fields.Many2one('account.report.report.grid', required=1)
    line_name = fields.Char(related='line_id.name', string='Rubrique', readonly=1)
    note    = fields.Text('Note', required=1)

    @api.multi
    def action_validate(self):
        self.env['account.report.report.grid.note'].create({
            'name'  : self.name,
            'note'  : self.note,
            'row_id': self.line_id.id,
        })
