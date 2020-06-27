# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

from odoo import fields, models, api


class ResCommune(models.Model):
    _name = 'res.commune'
    _descritpion = 'Commune'
    _order = 'name,id'

    code = fields.Char(string='Code Commune', size=2, help='Le code de la commune sur deux positions', required=True)
    state_id = fields.Many2one('res.country.state', string='Wilaya', required=True)            
    name = fields.Char(string='Commune', size=64, required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    commune_id = fields.Many2one('res.commune', string='Commune') 