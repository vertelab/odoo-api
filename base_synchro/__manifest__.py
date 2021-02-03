{
    "name": "Multi-DB Synchronization",
    "version": "12.0.0.3",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": "Multi-DB Synchronization",
    "author": "OpenERP SA, Serpent Consulting Services Pvt. Ltd.",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "contributors": ['Serpent Consulting Services Pvt. Ltd.', 'Harhu Technologies Pvt. Ltd.'],
    "website": "http://www.serpentcs.com",
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
