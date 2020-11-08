# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):

        if self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_picking') and (self.picking_type_id.name == "Livraisons" or self.picking_type_id.name == "Transferts internes"):
            raise UserError(
                _("you are not authorized to perform this action"))
            return
        if (self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out') and (self.picking_type_id.name == "Pick" or self.picking_type_id.name == "Réceptions"))\
                and not(self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out') and (self.picking_type_id.name == "Réceptions" and self.location_dest_id.name =="Output")):
            raise UserError(
                _("you are not authorized to perform this action"))
            return

        return super().button_validate()