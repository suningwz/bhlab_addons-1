# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    code_tiers   = fields.Char('Code tiers')
    # banque_id    = fields.Many2one('res.partner', string='Banque associée')
    employee     = fields.Boolean('Employé')
    num_agrement = fields.Char(u'N° CA/Agrement')
    rc  = fields.Char('R.C')
    nif = fields.Char('N.I.F', size=15)
    nis = fields.Char('N.I.S', size=15)
    ai  = fields.Char('Article d\'imposition')
    # code = fields.Char('Code')  # bessa
    fax = fields.Char('Fax')

