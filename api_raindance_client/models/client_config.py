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


class ApiRaindanceError(Exception):
    pass


class ClientConfig(models.Model):
    _name = 'api.raindance.client.config'
    _rec_name = 'url'
    _order = 'sequence, id'
    _suffix_url = ''

    sequence = fields.Integer()
    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[('u1', 'U1'),
                                              ('i1', 'I1'),
                                              ('t1', 'IT'),
                                              ('t2', 'T2'),
                                              ('prod', 'PROD'), ],
                                   string='Environment',
                                   default='u1',
                                   required=True)
    request_history_ids = fields.One2many('api.raindance.request.history',
                                          'config_id',
                                          string='Requests')

    @api.model
    def request_call(self, method, url, payload=None,
                     headers=None, params=None):
        secret = {"client_secret": self.client_secret,
                  "client_id": self.client_id}
        if params:
            params.update(secret)
        else:
            params = secret
        response = requests.request(method=method,
                                    url=url,
                                    data=payload,
                                    headers=headers,
                                    params=params)
        self.create_request_history(method=method,
                                    url=url,
                                    response=response,
                                    payload=payload,
                                    headers=headers,
                                    params=params)
        if response.status_code != 200:
            raise ApiRaindanceError(response.text)
        return response

    @api.model
    def create_request_history(self, method, url, response, payload=None,
                               headers=None, params=None):
        values = {'config_id': self.id,
                  'method': method,
                  'url': url,
                  'payload': payload,
                  'request_headers': headers,
                  'response_headers': response.headers,
                  'params': params,
                  'response_code': response.status_code}
        values.update(message=json.loads(response.content))
        self.env['api.raindance.request.history'].create(values)
        self._cr.commit()

    @api.model
    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {'x-amf-mediaType': "application/json",
                   'AF-TrackingId': tracking_id,
                   'AF-SystemId': "AF-SystemId",
                   'AF-EndUserId': "AF-EndUserId",
                   'AF-Environment': self.environment}
        return headers

    @api.model
    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url[1:]
        else:
            url = self.url
        url += self._suffix_url
        if path[0] != '/':
            url += '/'
        url += path
        return url

    def get_invoices(self, supplier_id=None, date=None):
        url = self.get_url('/invoices')
        payload = {}
        if supplier_id:
            payload.update({'supplier_id': supplier_id})
        if date:
            payload.update({'date': date})
        response = self.request_call(
            method="GET",
            url=url,
            payload=json.dumps(payload),
            headers=self.get_headers())

        return response

    def get_invoice(self, invoice_id):
        url = self.get_url('/invoices/%s' % invoice_id)
        payload = {}
        response = self.request_call(
            method="GET",
            url=url,
            payload=json.dumps(payload),
            headers=self.get_headers())
        return response

    def verify_config_is_set(self):
        return all(
            (self.url, self.environment, self.client_id, self.client_secret))

    def testing_get_invoices(self):
        return self.get_invoices()

    def testing_get_invoice(self):
        return self.get_invoice('758492')
