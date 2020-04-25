# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountCloture(models.Model):
    _name        = 'account.cloture'
    _description = 'Procedure de cloture'
    # _order       = 'name'

    @api.depends('jrn_cloture', 'jrn_ouverture', 'jrn_regroupement')
    def _soldes(self):
        for rec in self:
            rec.cloture_credit = sum(line.credit for line in rec.jrn_cloture)
            rec.cloture_debit  = sum(line.debit  for line in rec.jrn_cloture)
            rec.ouvert_credit  = sum(line.credit for line in rec.jrn_ouverture)
            rec.ouvert_debit   = sum(line.debit  for line in rec.jrn_ouverture)
            rec.regroup_credit = sum(line.credit for line in rec.jrn_regroupement)
            rec.regroup_debit  = sum(line.debit  for line in rec.jrn_regroupement)

    @api.one
    @api.depends('piece_ids')
    def _nbr_piece(self):
        for rec in self:
            if rec.piece_ids:
                rec.nbr_piece = len(rec.piece_ids)
            else:
                rec.nbr_piece = 0

    name             = fields.Char(u'Numéro', readonly=True)
    exercice_id      = fields.Many2one('account.exercice', string='Exercice', required=True, readonly=1, states={'new': [('readonly', False)]})
    exercice         = fields.Char(related='exercice_id.name', size=4, readonly=True)
    date             = fields.Date('Date', readonly=1, states={'new': [('readonly', False)]})
    currency_id      = fields.Many2one('res.currency', string='devise', default=lambda self: self.env.user.company_id.currency_id.id)
    cloture_debit    = fields.Monetary(compute=_soldes, string='Cloture - Débit', currency_field='currency_id')
    cloture_credit   = fields.Monetary(compute=_soldes, string='Cloture - Crédit', currency_field='currency_id')
    ouvert_debit     = fields.Monetary(compute=_soldes, string='Ouverture - Débit', currency_field='currency_id')
    ouvert_credit    = fields.Monetary(compute=_soldes, string='Ouverture - Crédit', currency_field='currency_id')
    regroup_debit    = fields.Monetary(compute=_soldes, string='Regroupement - Débit', currency_field='currency_id')
    regroup_credit   = fields.Monetary(compute=_soldes, string='Regroupement - Crédit', currency_field='currency_id')
    piece_ids        = fields.One2many('account.cloture.move.draft', 'cloture_id', string=u'Pieces non cloturées', readonly=1)
    nbr_piece        = fields.Integer(compute=_nbr_piece)
    jrn_cloture      = fields.One2many('account.cloture.cloture.journal', 'cloture_id', string='Journal cloture', readonly=1)
    jrn_ouverture    = fields.One2many('account.cloture.ouverture.journal', 'cloture_id', string=u'Journal de réouverture', readonly=1)
    jrn_regroupement = fields.One2many('account.cloture.regroupement.journal', 'cloture_id',
                                       string='Journal de regroupement', readonly=1)

    piece_ouverture_id = fields.Many2one('account.move', string='Piece (Ouverture)', readonly=True)
    piece_cloture_id = fields.Many2one('account.move', string='Piece (Cloture)', readonly=True)
    piece_regroup_id = fields.Many2one('account.move', string='Piece (Regroupement)', readonly=True)

    jrn_cloture_id   = fields.Many2one('account.journal', string='Journal cloture', required=True, readonly=1, states={'new': [('readonly', False)], 'controle': [('readonly', False)]})
    jrn_ouverture_id = fields.Many2one('account.journal', string='Journal réouverture', required=True, readonly=1, states={'new': [('readonly', False)], 'controle': [('readonly', False)]})
    jrn_regroupement_id = fields.Many2one('account.journal', string='Journal regroupement', readonly=1, states={'new': [('readonly', False)], 'controle': [('readonly', False)]})

    state = fields.Selection([('new', 'Nouveau'),
                              ('controle', 'Controle et Validation des journaux'),
                              ('cloture', 'Appliquation et cloture'),
                              ('done', 'Terminé'), ], string='Avancement', default='new')

    @api.model
    def create(self, vals):
        ex = vals['exercice_id']
        exe = self.env['account.exercice'].browse(ex)
        vals['name'] = 'Cloture/' + exe.name
        return super(AccountCloture, self).create(vals)

    @api.onchange('exercice_id')
    def onchange_exercice(self):
        if self.exercice_id:
            self.date = self.exercice_id.date_fin

    @api.one
    def create_journaux(self):
        # utilisé dans le cas ou le journal regroupement n'est pas utilisé
        pas_regroupement = False
        jrn_reg = self.jrn_regroupement_id.id
        if not self.jrn_regroupement_id:
            pas_regroupement = True
            jrn_reg = self.jrn_cloture_id.id

        self.create_pieces_ouvertes()
        self.jrn_cloture.unlink()
        self.jrn_ouverture.unlink()
        self.jrn_regroupement.unlink()
        if len(self.piece_ids) == 0:
            req = "select account_account.id, account_account.name, account_account.code, account_account.name, sum(debit), sum(credit), sum(debit)-sum(credit) as solde from account_move_line, account_account " \
                  "where account_move_line.account_id = account_account.id " \
                  "and journal_id <> %s " \
                  "and journal_id <> %s " \
                  "and date between %s and %s " \
                  "and code between '0' and '577777777' " \
                  "group by account_account.id, account_account.name, account_account.code, account_account.name " \
                  "order by account_account.code; "

            self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice+'-01-01', self.exercice+'-12-31',))
            res = self._cr.dictfetchall()
            i = 0

            for rec in res:
                if rec.get('solde') != 0.0:
                    i += 1
                    s_debit = 0.0
                    s_credit = 0.0
                    if rec.get('solde') > 0.0:
                        s_debit = rec.get('solde')
                    else:
                        s_credit = -1 * rec.get('solde')

                    self.env['account.cloture.cloture.journal'].create({
                        'name'       : i,
                        'account_id' : rec.get('id'),
                        'libelle'    : rec.get('name'),
                        'code'       : rec.get('code'),
                        'partner_id' : None,
                        'debit'      : s_debit,
                        'credit'     : s_credit,
                        'cloture_id' : self.id,
                    })
    # ouverture
            req = "select account_account.id, account_account.name, account_account.code, account_account.name, partner_id, sum(debit), sum(credit), sum(debit)-sum(credit) as solde from account_move_line, account_account " \
                  "where account_move_line.account_id = account_account.id " \
                  "and journal_id <> %s " \
                  "and journal_id <> %s " \
                  "and date between %s and %s " \
                  "and code between '0' and '577777777' " \
                  "group by account_account.id, account_account.name, account_account.code, account_account.name, partner_id " \
                  "order by account_account.code; "

            self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice+'-01-01', self.exercice+'-12-31',))
            res = self._cr.dictfetchall()
            i = 0

            for rec in res:
                if rec.get('solde') != 0.0:
                    i += 1
                    s_debit = 0.0
                    s_credit = 0.0
                    if rec.get('solde') > 0.0:
                        s_debit = rec.get('solde')
                    else:
                        s_credit = -1 * rec.get('solde')

                    self.env['account.cloture.ouverture.journal'].create({
                        'name'       : i,
                        'account_id' : rec.get('id'),
                        'libelle'    : rec.get('name'),
                        'code'       : rec.get('code'),
                        'partner_id' : rec.get('partner_id') or None,
                        'debit'      : s_debit,
                        'credit'     : s_credit,
                        'cloture_id' : self.id,
                    })

    # regroupement
    #         préparation des deux chiffres
            if not pas_regroupement:
                req = "select distinct LEFT(account_account.code,2) as cd from account_move_line, account_account " \
                      "where account_move_line.account_id = account_account.id " \
                      "and journal_id <> %s and journal_id <> %s and date between %s and %s "\
                      "and code between '6' and '799999999' order by cd;"

                self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice + '-01-01', self.exercice + '-12-31',))
                res = self._cr.dictfetchall()
                i = 0

                for rec in res:
                    deux = self.env['account.account'].search([('code', '=', rec.get('cd'))])
                    if deux.exists():
                        i += 1
                        self.env['account.cloture.regroupement.journal'].create({
                            'name'       : i,
                            'account_id' : deux.id,
                            'libelle'    : deux.name,
                            'code'       : deux.code,
                            'partner_id' : None,
                            'debit'      : 0,
                            'credit'     : 0,
                            'cloture_id' : self.id,
                        })

                # ecritures
                req = "select account_account.id, account_account.name, account_account.code, account_account.name, sum(debit) as debit, sum(credit) as credit, sum(debit) - sum(credit) as solde " \
                      "from account_move_line, account_account " \
                      "where account_move_line.account_id = account_account.id " \
                      "and journal_id <> %s " \
                      "and journal_id <> %s " \
                      "and date between %s and %s " \
                      "and code between '6' and '799999999999' " \
                      "group by account_account.id, account_account.name, account_account.code, account_account.name " \
                      "order by account_account.code; "

                self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice+'-01-01', self.exercice+'-12-31',))
                res = self._cr.dictfetchall()
                i = 0

                for rec in res:
                    i += 1
                    cpt = rec.get('code')
                    cpt_2 = self.env['account.cloture.regroupement.journal'].search([('cloture_id', '=', self.id), ('code', '=', cpt[:2])])
                    if cpt_2.exists:
                        if rec.get('solde') != 0.0:
                            s_debit = 0.0
                            s_credit = 0.0
                            if rec.get('solde') > 0.0:
                                s_debit = rec.get('solde')
                            else:
                                s_credit = -1 * rec.get('solde')

                            cpt_2.debit  += s_credit
                            cpt_2.credit += s_debit
                            if cpt_2.credit != 0.0 and cpt_2.debit != 0.0:
                                s = cpt_2.debit - cpt_2.credit
                                if s > 0:
                                    cpt_2.debit  = s
                                    cpt_2.credit = 0.0
                                else:
                                    cpt_2.debit  = 0.0
                                    cpt_2.credit = -1 * s

                            self.env['account.cloture.regroupement.journal'].create({
                                'name'       : i,
                                'account_id' : rec.get('id'),
                                'libelle'    : rec.get('name'),
                                'code'       : rec.get('code'),
                                'partner_id' : rec.get('partner_id') or None,
                                'debit'      : s_debit,
                                'credit'     : s_credit,
                                'cloture_id' : self.id,
                            })

            self.state = 'controle'

        # else:
        #     raise UserError(_(u'Il reste encore des pieces comptables non validées ! \n\n  Veuillez les traiter avant de lancer l\'opération de cloture !'))

    @api.multi
    def unlink(self):
        if self.state == 'done':
            raise UserError(_(u'Suppression non autorisée ! \n\n  l\'opération est déjà validée !'))
        else:
            self.jrn_regroupement.unlink()
            self.jrn_cloture.unlink()
            self.jrn_ouverture.unlink()
            self.piece_ids.unlink()
            rec = super(AccountCloture, self).unlink()
        return rec

    @api.multi
    def action_valider(self):
        self.state = 'cloture'

    @api.one
    def create_new_exercice(self):
        # cloturer l'exercice'
        old = self.env['account.exercice'].search([('name', '=', str(self.exercice))])
        if old.exists():
            old.state = 'done'
        # positionner lock_date
        self.env['account.change.lock.date'].create({
            'period_lock_date': '31-12-' + self.exercice,
            'fiscalyear_lock_date': '31-12-' + self.exercice,
        })

        # créer le nouvel exercice
        exe = self.env['account.exercice'].search([('name', '=', str(int(self.exercice) + 1))])
        if not exe.exists():
            new = self.env['account.exercice'].create({
                'name' : str(int(self.exercice) + 1),
            })
            new.action_create_periodes()

    @api.multi
    def action_done(self):
        self.state = 'done'
        self.create_new_exercice()
        # cloture
        cloture = self.env['account.move'].create({
            'ref': 'Cloture ' + self.exercice,
            'journal_id': self.jrn_cloture_id.id,
            'quantity' : 1.0,
            'state' : 'posted',
            'date': '31-12-' + self.exercice,
            'name': self.jrn_cloture_id.code + '/' + self.exercice + '/1',
        })
        line = []
        for rec in self.jrn_cloture:
            line.append({
                'account_id': rec.account_id.id,
                'name': rec.libelle,
                'partner_id': rec.partner_id.id or None,
                'debit': rec.debit,
                'credit': rec.credit,
                'move_id': cloture.id,
            })
        cloture.line_ids = line
        self.piece_cloture_id = cloture.id
        # regroupement
        if self.jrn_regroupement_id:
            regroup = self.env['account.move'].create({
                'ref': 'Regroupement ' + self.exercice,
                'journal_id': self.jrn_regroupement_id.id,
                'quantity': 1.0,
                'state': 'posted',
                'date': '01-01-' + self.exercice,
                'name': self.jrn_regroupement_id.code + '/' + self.exercice + '/1',
            })
            line = []
            for rec in self.jrn_regroupement:
                line.append({
                    'account_id': rec.account_id.id,
                    'name': rec.libelle,
                    'partner_id': rec.partner_id.id or None,
                    'debit': rec.debit,
                    'credit': rec.credit,
                    'move_id': regroup.id,
                })
            regroup.line_ids = line
            self.piece_regroup_id = regroup.id
        # réouverture
        ouverture = self.env['account.move'].create({
            'ref': 'Réverture ' + str(int(self.exercice)+1),
            'journal_id': self.jrn_ouverture_id.id,
            'quantity' : 1.0,
            'state' : 'posted',
            'date': '01-01-' + str(int(self.exercice)+1),
            'name': self.jrn_ouverture_id.code + '/' + str(int(self.exercice)+1) + '/1',
        })
        line = []
        for rec in self.jrn_ouverture:
            line.append({
                'account_id': rec.account_id.id,
                'name': rec.libelle,
                'partner_id': rec.partner_id.id or None,
                'debit': rec.debit,
                'credit': rec.credit,
                'move_id': ouverture.id,
            })
        ouverture.line_ids = line
        self.piece_ouverture_id = ouverture.id

    @api.one
    def create_pieces_ouvertes(self):
        # utilisé dans le cas ou le journal regroupement n'est pas utilisé
        jrn_reg = self.jrn_regroupement_id.id
        if not self.jrn_regroupement_id:
            jrn_reg = self.jrn_cloture_id.id

        req = "select id from account_move " \
              "where state = 'draft' " \
              "and journal_id <> %s " \
              "and journal_id <> %s " \
              "and date between %s and %s; "

        self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice+'-01-01', self.exercice+'-12-31',))
        res = self._cr.dictfetchall()
        i = 0
        self.piece_ids.unlink()
        for rec in res:
            i += 1
            self.env['account.cloture.move.draft'].create({
                'name'       : i,
                'move_id'    : rec.get('id'),
                'cloture_id' : self.id,
            })

    @api.one
    def valider_pieces_ouvertes(self):
        # utilisé dans le cas ou le journal regroupement n'est pas utilisé
        jrn_reg = self.jrn_regroupement_id.id
        if not self.jrn_regroupement_id:
            jrn_reg = self.jrn_cloture_id.id

        req = "update account_move set state='posted' " \
              "where state = 'draft' " \
              "and journal_id <> %s " \
              "and journal_id <> %s " \
              "and date between %s and %s; "

        self._cr.execute(req, (self.jrn_cloture_id.id, jrn_reg, self.exercice+'-01-01', self.exercice+'-12-31',))
        self.create_pieces_ouvertes()


class AccountClotureClotureJournal(models.Model):
    _name = 'account.cloture.cloture.journal'
    _description = 'Journal de cloture'
    _order = 'code'

    name       = fields.Integer('Numero')
    account_id = fields.Many2one('account.account', string='Compte')
    code       = fields.Char('Code')
    libelle    = fields.Char('Libellé')
    partner_id = fields.Many2one('res.partner', string='Tiers')
    debit      = fields.Monetary('Debit', currency_field='currency_id')
    credit     = fields.Monetary('Credit', currency_field='currency_id')
    cloture_id = fields.Many2one('account.cloture', string='Cloture')
    currency_id = fields.Many2one(related='cloture_id.currency_id')


class AccountClotureOuvertureJournal(models.Model):
    _name = 'account.cloture.ouverture.journal'
    _description = 'Journal de reouverture'
    _order = 'code'

    name       = fields.Integer('Numero')
    account_id = fields.Many2one('account.account', string='Compte')
    code       = fields.Char('Code')
    libelle    = fields.Char('Libellé')
    partner_id = fields.Many2one('res.partner', string='Tiers')
    debit      = fields.Monetary('Debit', currency_field='currency_id')
    credit     = fields.Monetary('Credit', currency_field='currency_id')
    cloture_id = fields.Many2one('account.cloture', string='Cloture')
    currency_id = fields.Many2one(related='cloture_id.currency_id')


class AccountClotureRegroupementJournal(models.Model):
    _name = 'account.cloture.regroupement.journal'
    _description = 'Journal de regroupement'
    _order = 'code'

    name       = fields.Integer('Numero')
    account_id = fields.Many2one('account.account', string='Compte')
    code       = fields.Char('Code')
    libelle    = fields.Char('Libellé')
    partner_id = fields.Many2one('res.partner', string='Tiers')
    debit      = fields.Monetary('Debit', currency_field='currency_id')
    credit     = fields.Monetary('Credit', currency_field='currency_id')
    cloture_id = fields.Many2one('account.cloture', string='Cloture')
    currency_id = fields.Many2one(related='cloture_id.currency_id')


class AccountCloturePieceOuverte(models.Model):
    _name = 'account.cloture.move.draft'
    _description = 'Piece non valide'
    _order = 'journal_id,date'

    name       = fields.Integer('Numero', readonly=True)
    move_id    = fields.Many2one('account.move', string='Piece', readonly=True)
    ref        = fields.Char(related='move_id.ref', string=u'Référence', readonly=True)
    date       = fields.Date(related='move_id.date', string='Date', readonly=True)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', readonly=True)
    state      = fields.Selection(related='move_id.state', string='Etat', readonly=True)
    cloture_id = fields.Many2one('account.cloture', string='Cloture')
