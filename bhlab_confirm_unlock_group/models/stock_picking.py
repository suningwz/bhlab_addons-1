# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_picking') \
                and (self.picking_type_id.name == "Réceptions" or self.picking_type_id.name == "Pick"):
            return super().button_validate()
        else :
            if (self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out')
                and (self.picking_type_id.name == "Transferts internes" or self.picking_type_id.name == "Livraisons"))\
                or (self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out')
                        and (self.picking_type_id.name == "Réceptions" and self.location_dest_id.name =="Output")):
                return super().button_validate()
        raise UserError(
            _("you are not authorized to perform this action"))

    def action_cancel(self):
        if self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_picking') \
                and (self.picking_type_id.name == "Réceptions" or self.picking_type_id.name == "Pick"):
            return super().action_cancel()
        else :
            if (self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out')
                and (self.picking_type_id.name == "Transferts internes" or self.picking_type_id.name == "Livraisons"))\
                or (self.env.user.has_group('bhlab_confirm_unlock_group.group_allow_confirm_out')
                        and (self.picking_type_id.name == "Pick" and self.location_dest_id.name =="Stock")):
                return super().button_validate()
        raise UserError(
            _("you are not authorized to perform this action"))

