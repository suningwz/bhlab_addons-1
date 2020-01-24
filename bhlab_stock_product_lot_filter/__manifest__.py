# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "bhlab Stock filter lots and products",
    "summary": "In picking out lots' selection, "
               "filter product and lot based on their location and seller",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "author": "nadir BHLab",
    "application": False,
    "installable": True,
    "depends": [
        "stock","purchase",
    ],
    "data": [
        "views/stock_move_line_view.xml",
        "views/stock_picking_view.xml",
        "views/purchase_order_view.xml",
    ]
}
