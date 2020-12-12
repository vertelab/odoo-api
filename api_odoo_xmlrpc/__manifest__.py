{
    "name": "API Odoo XMLRPC - Sync data",
    "version": "12.0.0.2",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": "Exchange Data between servers",
    "author": "Vertel AB",
    "website": "https://vertel.se/",
    "description": "Module to sync data",
    "depends": [
        "base_setup",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/api_odoo_synchro_view.xml",
        "views/api_odoo_synchro_view.xml",
        "views/res_request_view.xml",
    ],
    "installable": True,
}
