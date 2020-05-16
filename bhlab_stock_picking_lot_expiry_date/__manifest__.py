# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BHlab Stock picking lot & Exipry date",
    "summary": " ",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "12.0/stock_EoL_lot",
    "author": "Nadir",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock","product",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/production_lot_view.xml",
        "views/quant_view.xml",
        "views/stock_location_view.xml",
        "views/stock_inventory_view.xml",
        "views/product_template_views.xml",
        "views/stock_inventory_detail_view.xml",
        "views/res_config_settings_views.xml",
    ]
}
