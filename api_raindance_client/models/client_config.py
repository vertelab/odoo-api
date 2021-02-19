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
    _name = "api.raindance.client.config"
    _rec_name = "url"
    _order = "sequence, id"
    _suffix_url = ""

    sequence = fields.Integer()
    url = fields.Char(string="Url", required=True)
    client_secret = fields.Char(string="Client Secret", required=True)
    client_id = fields.Char(string="Client ID", required=True)
    environment = fields.Selection(
        selection=[
            ("U1", "U1"),
            ("I1", "I1"),
            ("T1", "T1"),
            ("T2", "T2"),
            ("PROD", "PROD"),
        ],
        string="Environment",
        default="U1",
        required=True,
    )
    request_history_ids = fields.One2many(
        "api.raindance.request.history", "config_id", string="Requests"
    )

    @api.model
    def request_call(self, method, url, payload=None, headers=None, params=None):
        secret = {"client_secret": self.client_secret, "client_id": self.client_id}
        if params:
            params.update(secret)
        else:
            params = secret
        _logger.warn("DAER payload: %s" % payload)
        response = requests.request(
            method=method,
            url=url,
            data=payload,
            headers=headers,
            params=params,
            verify=False,
        )
        _logger.warn("DAER response: %s: %s" % (response.status_code, response.text))
        self.create_request_history(
            method=method,
            url=url,
            response=response,
            payload=payload,
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise ApiRaindanceError("%s: %s" % (response.status_code, response.text))
        return response

    @api.model
    def create_request_history(
        self, method, url, response, payload=None, headers=None, params=None
    ):
        values = {
            "config_id": self.id,
            "method": method,
            "url": url,
            "payload": payload,
            "request_headers": headers,
            "response_headers": response.headers,
            "params": params,
            "response_code": response.status_code,
        }
        try:
            values.update(message=json.loads(response.content))
        except:
            pass
        self.env["api.raindance.request.history"].create(values)
        self._cr.commit()

    @api.model
    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {'Content-Type': "application/json",
                   'AF-TrackingId': tracking_id,
                   'AF-SystemId': "AFDAFA",
                   'AF-EndUserId': "*sys*",
                   'AF-Environment': self.environment}
        return headers

    @api.model
    def get_url(self, path):
        if self.url[-1] == "/":
            url = self.url + path
        else:
            url = self.url + "/" + path
        _logger.warn(url)
        return url

    def get_invoices(self, order_id=None):
        url = self.get_url('/orders')
        params = {'order_id': order_id}
        response = self.request_call(
            method="GET",
            url=url,
            headers=self.get_headers(),
            params=params
            )
        return response

    def get_invoice(self, invoice_id):
        url = self.get_url("invoices/%s" % invoice_id)
        payload = {}
        response = self.request_call(
            method="GET",
            url=url,
            payload=json.dumps(payload),
            headers=self.get_headers(),
        )
        return response

    def verify_config_is_set(self):
        return all((self.url, self.environment, self.client_id, self.client_secret))

    def testing_get_invoices(self):
        return self.get_invoices(123, "200220")

    def testing_get_invoice(self):
        return self.get_invoice("758492")
