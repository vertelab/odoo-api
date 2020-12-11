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

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _name = 'ipf.tlr.client.config'
    _description = 'tlr ipf client'
    _rec_name = 'url'
    _suffix_url = '/v1'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[
        ('U1', 'U1'),
        ('I1', 'I1'),
        ('T1', 'IT'),
        ('T2', 'T2'),
        ('PROD', 'PROD'),
    ], string='Environment',
        default='u1',
        required=True)
    request_history_ids = fields.One2many(
        'ipf.tlr.request.history',
        'config_id',
        string='Requests')

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

        response = requests.request(
            method=method,
            url=url,
            data=payload,
            headers=headers,
            params=params,
            verify=False
        )

        self.create_request_history(
            method=method,
            url=url,
            response=response,
            payload=payload,
            headers=headers,
            params=params
        )

        return response

    def create_request_history(self, method, url, response, payload=None,
                               headers=None, params=None):
        values = {
            'config_id': self.id,
            'method': method,
            'url': url,
            'payload': payload,
            'request_headers': headers,
            'response_headers': response.headers,
            'params': params,
            'response_code': response.status_code,
        }
        try:
            values.update(message=response.text)
        except json.decoder.JSONDecodeError:
            pass
        self.env['ipf.tlr.request.history'].create(values)

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'x-amf-mediaType': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "AF-SystemId",
            'AF-EndUserId': "AF-EndUserId",
            'AF-Environment': self.environment,
        }
        return headers

    def get_url(self, path):
        url = ''
        if self.url[-1] == '/':
            url = self.url[1:]
        else:
            url = self.url
        url += self._suffix_url
        if path[0] != '/':
            url += '/'
        url += path
        return url

    def get_request(self, url, query=None):
        querystring = {
            "client_secret": self.client_secret,
            "client_id": self.client_id
        }
        if query:
            querystring.update(query)
        url = self.get_url(url)
        response = self.request_call(
            method="GET",
            url=url,
            headers=self.get_headers(),
            params=querystring
        )
        return response

    def get_uppfoljningskategorier(self):
        return self.get_request('/lista/uppfoljningskategorier')

    def get_tjanstekategorier(self):
        return self.get_request('/lista/tjanstekategorier')

    def get_tjanster(self):
        return self.get_request('/lista/tjanster')

    def get_tjanstekategori_id(self):
        object_id = '2345'
        return self.get_request('/lista/tjanster/%s' % object_id)

    def get_leveransomraden(self):
        return self.get_request('/lista/leveransomraden')

    def get_tjanst_id(self):
        object_id = '2345'
        return self.get_request('/lista/leveransomraden/%s' % object_id)

    def get_tjansteleverantorerd(self):
        return self.get_request('/lista/tjanstekategorier')

    def get_sprak(self):
        return self.get_request('/lista/sprak')

    def get_tjansteleverantorer(self):
        object_id = '2345'
        return self.get_request('/lista/tjansteleverantorer/%s' % object_id)

    def get_texter(self):
        return self.get_request('/lista/texter')

    def get_avropsTyp(self):
        return self.get_request('/lista/avropsTyp')

    def get_betalmodellTyp(self):
        return self.get_request('/lista/betalmodellTyp')

    def get_yrkesinriktning(self):
        return self.get_request('/lista/yrkesinriktning')

    def get_utforandeVerksamhet(self):
        query = {
            'tjanstekod_lista': 'tjanstekod_lista',
            'postort': 'postort',
            'nyckel': 'nyckel,nyckel',
            'varde': 'varde,varde',
            'rating': '2,3,4,5',
            'sidnummer': '2345',
            'sidstorlek': '2345',
        }
        return self.get_request('/sok/utforandeVerksamhet', query)

    def get_organisationsnummer(self):
        object_id = '2345'
        return self.get_request('/sok/utforandeVerksamhet/%s' % object_id)

    def get_utforandeVerksamhetMedKoordinater(self):
        query = {
            'tjanstekod_lista': 'tjanstekod_lista',
            'postort': 'postort',
            'nyckel': 'nyckel,nyckel',
            'varde': 'varde,varde',
            'rating': '2,3,4,5',
            'sidnummer': '2345',
            'sidstorlek': '2345',
            'latitud': '2345',
            'longitud': '2345',
            'max_avstand': '2345',
        }
        return self.get_request('/sok/utforandeVerksamhetMedKoordinater', query)

    def get_tjanst(self):
        object_id = '2345'
        return self.get_request('/hamta/tjanst/%s' % object_id)

    def get_utforande_verksamhet_id(self):
        object_id = '2345'
        return self.get_request('/hamta/utforandeVerksamhet/%s' % object_id)

    def get_adress(self):
        object_id = '2345'
        return self.get_request('/hamta/adress/%s' % object_id)

    def get_deklaration(self):
        object_id = '2345'
        return self.get_request('/hamta/deklaration/%s' % object_id)

    def get_tjansteleverantor(self):
        object_id = '2345'
        return self.get_request('/hamta/get_tjansteleverantor/%s' % object_id)
