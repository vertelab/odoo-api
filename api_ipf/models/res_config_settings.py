# -*- coding: utf-8 -*-

from odoo import fields, models


class IpfResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_secret = fields.Char(string='Client Secret',
                                config_parameter='api_ipf.client_secret')
    client_id = fields.Char(string='Client ID',
                            config_parameter='api_ipf.client_id')
    system_id = fields.Char(string='System ID',
                            config_parameter='api_ipf.system_id')
    environment = fields.Selection(selection=[('u1', 'U1'),
                                              ('i1', 'I1'),
                                              ('t1', 'IT'),
                                              ('t2', 'T2'),
                                              ('prod', 'PROD'), ],
                                   string='Environment',
                                   default='u1',
                                   required=True,
                                   config_parameter='api_ipf.environment')
