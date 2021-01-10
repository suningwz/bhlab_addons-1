from odoo import models, fields, api

class confirm_wizard(models.TransientModel):
    _name = 'bhlab.confirm.wizard'
    _description = 'Exipry product Confirmation'

    @api.multi
    def yes(self):
        return True

    @api.multi
    def no(self):
        return False