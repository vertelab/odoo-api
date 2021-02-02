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
    environment = fields.Selection(selection=[('U1', 'U1'),
                                              ('I1', 'I1'),
                                              ('T1', 'IT'),
                                              ('T2', 'T2'),
                                              ('PROD', 'PROD'), ],
                                   string='Environment',
                                   default='U1',
                                   required=True,
                                   config_parameter='api_ipf.environment')
