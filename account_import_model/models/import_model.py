# -*- coding: utf-8 -*-

from odoo import models, fields, api


# liste des colonnes
def _get_liste(self):
    lst = []
    for a in range(65, 65 + 26):
        lst.append((chr(a), chr(a)))
    return lst


# class UseTo(models.Model):
#     _name = 'use.to'
#
#     name = fields.Char(u'Utilisé pour')


class AccountImportModel(models.Model):
    _name        = 'account.import.model'
    _order       = 'name'

    name             = fields.Char   ('Nom du modele', required=True)
    use_number_1     = fields.Selection([('nombre', 'les numeros de colonnes'),
                                         ('lettre', 'les noms des colonnes (lettres)')], string='Utiliser', default='lettre')
    # piece
    col_name         = fields.Integer(u'Numéro de la piece', default=-1, required=True)
    col_libelle      = fields.Integer(u'Libellé écrture', default=-1, required=True)
    col_ref          = fields.Integer(u'Référence', default=-1, required=True)
    col_date         = fields.Integer('Date'     , default=-1, required=True)
    col_journal      = fields.Integer('Journal'  , default=-1, required=True)
    col_partner      = fields.Integer('Tiers'    , default=-1, required=True)
    # col_currency_id       = fields.Integer('Marque'       , default=-1, required=True)
    # ecriture
    col_account      = fields.Integer('Compte'   , default=-1, required=True)
    col_debit        = fields.Integer(u'Débit'    , default=-1, required=True)
    col_credit       = fields.Integer(u'Crédit'   , default=-1, required=True)
    col_sequence     = fields.Integer(u'Ordre des écritures'   , default=-1, required=True)

    col_a_name       = fields.Selection(_get_liste, string=u'Numéro de la piece', required=True)
    col_a_libelle    = fields.Selection(_get_liste, string=u'Libellé écrture', required=True)
    col_a_ref        = fields.Selection(_get_liste, string=u'Référence')
    col_a_date       = fields.Selection(_get_liste, string='Date', required=True)
    col_a_journal    = fields.Selection(_get_liste, string='Journal', required=True)
    col_a_partner    = fields.Selection(_get_liste, string='Tiers', required=True)
    col_a_account    = fields.Selection(_get_liste, string='Compte', required=True)
    col_a_debit      = fields.Selection(_get_liste, string=u'Débit', required=True)
    col_a_credit     = fields.Selection(_get_liste, string=u'Crédit', required=True)
    col_a_sequence   = fields.Selection(_get_liste, string=u'Ordre des écritures', required=True)

    @api.onchange('col_a_name')
    def onchange_a_name(self):
        if self.col_a_name:
            self.col_name = ord(self.col_a_name) - 65
        else:
            self.col_name = -1

    @api.onchange('col_a_libelle')
    def onchange_a_libelle(self):
        if self.col_a_libelle:
            self.col_libelle = ord(self.col_a_libelle) - 65
        else:
            self.col_libelle = -1

    @api.onchange('col_a_ref')
    def onchange_a_ref(self):
        if self.col_a_ref:
            self.col_ref = ord(self.col_a_ref) - 65
        else:
            self.col_ref = -1

    @api.onchange('col_a_date')
    def onchange_a_date(self):
        if self.col_a_date:
            self.col_date = ord(self.col_a_date) - 65
        else:
            self.col_date = -1

    @api.onchange('col_a_journal')
    def onchange_a_journal (self):
        if self.col_a_journal :
            self.col_journal = ord(self.col_a_journal) - 65
        else:
            self.col_journal = -1

    @api.onchange('col_a_partner')
    def onchange_a_partner(self):
        if self.col_a_partner:
            self.col_partner = ord(self.col_a_partner) - 65
        else:
            self.col_partner = -1

    @api.onchange('col_a_account')
    def onchange_a_account(self):
        if self.col_a_account:
            self.col_account = ord(self.col_a_account) - 65
        else:
            self.col_account = -1

    @api.onchange('col_a_debit')
    def onchange_a_debit(self):
        if self.col_a_debit:
            self.col_debit = ord(self.col_a_debit) - 65
        else:
            self.col_debit = -1

    @api.onchange('col_a_credit')
    def onchange_a_credit(self):
        if self.col_a_credit:
            self.col_credit = ord(self.col_a_credit) - 65
        else:
            self.col_credit = -1

    @api.onchange('col_a_sequence')
    def onchange_a_sequence(self):
        if self.col_a_sequence:
            self.col_sequence= ord(self.col_a_sequence) - 65
        else:
            self.col_sequence = -1

    @api.onchange('col_name')
    def onchange_name(self):
        self.col_a_name = ''
        if 0 <= self.col_name <= 25:
            self.col_a_name = chr(self.col_name + 65)

    @api.onchange('col_libelle')
    def onchange_libelle(self):
        self.col_a_libelle = ''
        if 0 <= self.col_libelle <= 25:
            self.col_a_libelle = chr(self.col_libelle + 65)

    @api.onchange('col_ref')
    def onchange_ref(self):
        self.col_a_ref = ''
        if 0 <= self.col_ref <= 25:
            self.col_a_ref = chr(self.col_ref + 65)

    @api.onchange('col_date')
    def onchange_date(self):
        self.col_a_date = ''
        if 0 <= self.col_date <= 25:
            self.col_a_date = chr(self.col_date + 65)

    @api.onchange('col_journal')
    def onchange_journal(self):
        self.col_a_journal = ''
        if 0 <= self.col_journal <= 25:
            self.col_a_journal = chr(self.col_journal + 65)

    @api.onchange('col_partner')
    def onchange_partner(self):
        self.col_a_partner = ''
        if 0 <= self.col_partner <= 25:
            self.col_a_partner = chr(self.col_partner + 65)

    @api.onchange('col_account')
    def onchange_account(self):
        self.col_a_account = ''
        if 0 <= self.col_account <= 25:
            self.col_a_account = chr(self.col_account + 65)

    @api.onchange('col_debit')
    def onchange_debit(self):
        self.col_a_debit = ''
        if 0 <= self.col_debit <= 25:
            self.col_a_debit = chr(self.col_debit + 65)

    @api.onchange('col_credit')
    def onchange_credit(self):
        self.col_a_credit = ''
        if 0 <= self.col_credit <= 25:
            self.col_a_credit = chr(self.col_credit + 65)

    @api.onchange('col_sequence')
    def onchange_sequence(self):
        self.col_a_sequence = ''
        if 0 <= self.col_sequence <= 25:
            self.col_a_sequence = chr(self.col_sequence + 65)
