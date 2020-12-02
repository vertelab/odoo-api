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

import logging
import json
from odoo import http, api
from .token import \
    validate, valid_response, invalid_response
from .xml_response_template import xml_response

_logger = logging.getLogger(__name__)


class IpfReportServer(http.Controller):
    _suffix_url = '/api/v1'

    @api.model
    def validating_params(self, params, kwargs):
        """Checking params
                 (param[str], required[boolean], type, array[boolean])"""
        missed_required = []
        errors = []
        type_match = {'string': str, 'integer': int}
        for param_prop in params:
            if not kwargs.get(param_prop[0]) and param_prop[1]:
                missed_required.append(param_prop[0])
            elif kwargs.get(param_prop[0]) and param_prop[2]:
                value = kwargs[param_prop[0]]
                if len(param_prop) == 4 and param_prop[3]:
                    values = value.split(',')
                else:
                    values = [value]
                for value in values:
                    try:
                        type_match[param_prop[2]](value)
                    except Exception:
                        message = 'Parameter %s is not %s' % (
                            param_prop[0], param_prop[2])
                        errors.append(message)
                        break
        if missed_required:
            errors.append('Missed required fields')
        return missed_required, errors

    @api.model
    def validating_number(self, field_name, value):
        if not value.isdigit():
            return invalid_response(
                'Bad request', '%s is not number' % field_name, 403)

    @api.model
    def example_response(self, name):
        return valid_response(xml_response[name])

    @validate
    @http.route(_suffix_url + "/lista/uppfoljningskategorier", methods=["GET"],
                type="http", auth="none", csrf=False)
    def uppfoljningskategorier(self, *args, **kwargs):
        return self.example_response('uppfoljningskategorier')

    @validate
    @http.route(_suffix_url + "/lista/tjanstekategorier", methods=["GET"],
                type="http", auth="none", csrf=False)
    def tjanstekategorier(self, *args, **kwargs):
        return valid_response(xml_response['tjanstekategorier'])

    @validate
    @http.route(_suffix_url + "/lista/tjanster", methods=["GET"],
                type="http", auth="none", csrf=False)
    def tjanster(self, *args, **kwargs):
        return valid_response(xml_response['tjanster'])

    @validate
    @http.route(_suffix_url + "/lista/tjanster/<tjanstekategori_id>", methods=["GET"],
                type="http", auth="none", csrf=False)
    def tjanster_id(self, tjanstekategori_id, *args, **kwargs):
        return valid_response(xml_response['tjanster_id'])

    @validate
    @http.route(_suffix_url + "/lista/leveransomraden", methods=["GET"],
                type="http", auth="none", csrf=False)
    def leveransomraden(self, *args, **kwargs):
        return valid_response(xml_response['leveransomraden'])

    @validate
    @http.route(_suffix_url + "/lista/leveransomraden/<tjanst_id>", methods=["GET"],
                type="http", auth="none", csrf=False)
    def leveransomraden_id(self, tjanst_id, *args, **kwargs):
        return valid_response(xml_response['leveransomraden'])

    @validate
    @http.route(_suffix_url + "/lista/sprak", methods=["GET"],
                type="http", auth="none", csrf=False)
    def sprak(self, *args, **kwargs):
        return valid_response(xml_response['sprak'])

    @validate
    @http.route(_suffix_url + "/lista/tjansteleverantorer/<tjanstekod>", methods=["GET"],
                type="http", auth="none", csrf=False)
    def tjansteleverantorer(self, tjanstekod, *args, **kwargs):
        return valid_response(xml_response['tjansteleverantorer'])

    @validate
    @http.route(_suffix_url + "/lista/texter", methods=["GET"],
                type="http", auth="none", csrf=False)
    def texter(self, *args, **kwargs):
        return valid_response(xml_response['texter'])

    @validate
    @http.route(_suffix_url + "/lista/avropsTyp", methods=["GET"],
                type="http", auth="none", csrf=False)
    def avropsTyp(self, *args, **kwargs):
        return valid_response(xml_response['avropsTyp'])

    @validate
    @http.route(_suffix_url + "/lista/betalmodellTyp", methods=["GET"],
                type="http", auth="none", csrf=False)
    def betalmodellTyp(self, *args, **kwargs):
        return valid_response(xml_response['betalmodellTyp'])

    @validate
    @http.route(_suffix_url + "/lista/yrkesinriktning", methods=["GET"],
                type="http", auth="none", csrf=False)
    def yrkesinriktning(self, *args, **kwargs):
        return valid_response(xml_response['yrkesinriktning'])

    @validate
    @http.route(_suffix_url + "/sok/utforandeVerksamhet", methods=["GET"],
                type="http", auth="none", csrf=False)
    def utforande_verksamhet(self, *args, **kwargs):
        # validating_params -> (param[str], required[bool], type, array[bool])
        params = [
            ('tjanstekod_lista', True, 'string', True),
            ('postort', False, 'string'),
            ('nyckel', False, 'string', True),
            ('varde', False, False, True),
            ('rating', False, 'integer', True),
            ('sidnummer', True, 'integer'),
            ('sidstorlek', True, 'integer'),
        ]
        missed_required, errors = self.validating_params(params, kwargs)
        error_message, miss_req_message = '', ''
        if errors:
            error_message = '. '.join(errors)
        if missed_required:
            miss_req_message = 'Missed required fields: %s' % ','.join(
                missed_required)
        if error_message or miss_req_message:
            return invalid_response(error_message, miss_req_message)
        return valid_response(xml_response['utforandeVerksamhet'])

    @validate
    @http.route(_suffix_url + "/sok/utforandeVerksamhet/<organisationsnummer>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def organisationsnummer(self, organisationsnummer, *args, **kwargs):
        return valid_response(xml_response['organisationsnummer'])

    @validate
    @http.route(_suffix_url + "/sok/utforandeVerksamhetMedKoordinater", methods=["GET"],
                type="http", auth="none", csrf=False)
    def utforandeVerksamhetMedKoordinater(self, *args, **kwargs):
        # validating_params -> (param[str], required[bool], type[str or False], array[bool])
        params = [
            ('tjanstekod_lista', True, 'string', True),
            ('postort', False, 'string'),
            ('nyckel', False, 'string', True),
            ('varde', False, False, True),
            ('rating', False, 'integer', True),
            ('sidnummer', True, 'integer'),
            ('sidstorlek', True, 'integer'),
            ('latitud', True, 'integer'),
            ('longitud', True, 'integer'),
            ('max_avstand', True, 'integer'),
        ]
        missed_required, errors = self.validating_params(params, kwargs)
        error_message, miss_req_message = '', ''
        if errors:
            error_message = '. '.join(errors)
        if missed_required:
            miss_req_message = 'Missed required fields: %s' % ','.join(
                missed_required)
        if error_message or miss_req_message:
            return invalid_response(error_message, miss_req_message)
        return valid_response(xml_response['utforandeVerksamhetMedKoordinater'])

    @validate
    @http.route(_suffix_url + "/hamta/tjanst/<tjanst_id>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def tjanst(self, tjanst_id, *args, **kwargs):
        self.validating_number('tjanst_id', tjanst_id)
        return valid_response(xml_response['tjanst'])

    @validate
    @http.route(_suffix_url + "/hamta/utforandeVerksamhet/<utforande_verksamhet_id>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def utforande_verksamhet_id(self, utforande_verksamhet_id, *args, **kwargs):
        self.validating_number(
            'utforande_verksamhet_id', utforande_verksamhet_id)
        return valid_response(xml_response['utforandeVerksamhet'])

    @validate
    @http.route(_suffix_url + "/hamta/adress/<adress_id>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def adress(self, adress_id, *args, **kwargs):
        self.validating_number('adress_id', adress_id)
        return valid_response(xml_response['adress'])

    @validate
    @http.route(_suffix_url + "/hamta/deklaration/<deklaration_id>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def deklaration(self, deklaration_id, *args, **kwargs):
        self.validating_number('deklaration_id', deklaration_id)
        return valid_response(xml_response['deklaration'])

    @validate
    @http.route(_suffix_url + "/hamta/tjansteleverantor/<tjansteleverantor_id>",
                methods=["GET"], type="http", auth="none", csrf=False)
    def tjansteleverantor(self, tjansteleverantor_id, *args, **kwargs):
        self.validating_number('tjansteleverantor_id', tjansteleverantor_id)
        return valid_response(xml_response['tjansteleverantor'])
