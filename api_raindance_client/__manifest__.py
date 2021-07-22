# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

{
    'name': 'API Raindance Client',
    'version': '12.0.0.0.5',
    'category': 'Tools',
    'description': """APi for connection between DAFA and Raindance \n
    
    v12.0.0.0.2 AFC-2560 Fixed better error message for API configuration.
    v12.0.0.0.3 AFC-2560 Added error message in one line and Improved code to fix error when success response.
    
    """,

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'images': [
        'static/description/icon.png'
    ],
    'depends': [
        'hr',
        'api_ipf'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/client_config_views.xml',
    ],
    'installable': True,
}
