﻿# -*- coding: utf-8 -*-

from odoo import exceptions, fields, models, api, _

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    code_tiers = fields.Char('Code tiers')
    employee = fields.Boolean('Employé')
    num_agrement = fields.Char(u'N° CA/Agrement')
    rc = fields.Char('R.C')
    nif = fields.Char('N.I.F', size=15)
    nis = fields.Char('N.I.S', size=15)
    ai = fields.Char('Article d\'imposition')
    fax = fields.Char('Fax')
