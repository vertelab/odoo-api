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
from odoo import http
from .token import \
    validate_token, valid_response, invalid_response

_logger = logging.getLogger(__name__)


class ApiRaindanceServer(http.Controller):

    @validate_token
    @http.route("/invoices", methods=["GET"],
                type="http", auth="none", csrf=False)
    def invoices(self, *args, **kwargs):
        values = http.request.httprequest.get_data()
        values_dict = json.loads(values.decode())
        missing_values = []
        response = {
            "invoices": [
                {
                    "id": "102934",
                    "invoice_number": "MEET-1",
                    "invoice_date": "2020-11-20",
                    "item_name": "Utbildning 1",
                    "case_number": "123",
                    "amount": 111
                },
                {
                    "id": "10300",
                    "invoice_number": "MEET-2",
                    "invoice_date": "2020-11-21",
                    "item_name": "Utbildning 2",
                    "case_number": "111",
                    "amount": 5000
                }
            ]
        }
        return valid_response(response)

    @validate_token
    @http.route("/invoices/<invoice_id>", methods=["GET"],
                type="http", auth="none", csrf=False)
    def invoice(self, invoice_id, **kwargs):
        response = {
            "svefaktura": "<Invoice xmlns:cac=\"urn:sfti:CommonAggregateComponents:1:0\" xmlns:cbc=\"urn:oasis:names:tc:ubl:CommonBasicComponents:1:0\" xmlns=\"urn:sfti:documents:BasicInvoice:1:0\">\r\n\t<ID>9100220</ID>\r\n\t<cbc:IssueDate>2020-02-11</cbc:IssueDate>\r\n\t<InvoiceTypeCode>380</InvoiceTypeCode>\r\n\t<InvoiceCurrencyCode>SEK</InvoiceCurrencyCode>\r\n\t<LineItemCountNumeric>1</LineItemCountNumeric>\r\n\t<cac:BuyerParty>\r\n\t\t<cac:Party>\r\n\t\t\t<cac:PartyIdentification>\r\n\t\t\t\t<cac:ID>2021002114</cac:ID>\r\n\t\t\t</cac:PartyIdentification>\r\n\t\t\t<cac:PartyName>\r\n\t\t\t\t<cbc:Name>Arbetsförmedlingen Skanningcentral</cbc:Name>\r\n\t\t\t</cac:PartyName>\r\n\t\t\t<cac:Address>\r\n\t\t\t\t<cbc:Postbox>Skanningcentral</cbc:Postbox>\r\n\t\t\t\t<cbc:CityName>KRISTINEHAMN</cbc:CityName>\r\n\t\t\t\t<cbc:PostalZone>68185</cbc:PostalZone>\r\n\t\t\t</cac:Address>\r\n\t\t\t<cac:PartyTaxScheme>\r\n\t\t\t\t<cac:CompanyID>2021002114</cac:CompanyID>\r\n\t\t\t\t<cac:TaxScheme>\r\n\t\t\t\t\t<cac:ID>SWT</cac:ID>\r\n\t\t\t\t</cac:TaxScheme>\r\n\t\t\t</cac:PartyTaxScheme>\r\n\t\t</cac:Party>\r\n\t</cac:BuyerParty>\r\n\t<cac:SellerParty>\r\n\t\t<cac:Party>\r\n\t\t\t<cac:PartyIdentification>\r\n\t\t\t\t<cac:ID>5565600854</cac:ID>\r\n\t\t\t</cac:PartyIdentification>\r\n\t\t\t<cac:PartyName>\r\n\t\t\t\t<cbc:Name>Se Eqv</cbc:Name>\r\n\t\t\t</cac:PartyName>\r\n\t\t\t<cac:Address>\r\n\t\t\t\t<cbc:StreetName>Norgegatan 1</cbc:StreetName>\r\n\t\t\t\t<cbc:CityName>Kista</cbc:CityName>\r\n\t\t\t\t<cbc:PostalZone>16432</cbc:PostalZone>\r\n\t\t\t</cac:Address>\r\n\t\t\t<cac:PartyTaxScheme>\r\n\t\t\t\t<cac:CompanyID>SE556560085401</cac:CompanyID>\r\n\t\t\t\t<cac:RegistrationAddress/>\r\n\t\t\t\t<cac:TaxScheme>\r\n\t\t\t\t\t<cac:ID>VAT</cac:ID>\r\n\t\t\t\t</cac:TaxScheme>\r\n\t\t\t</cac:PartyTaxScheme>\r\n\t\t\t<cac:PartyTaxScheme>\r\n\t\t\t\t<cbc:RegistrationName>Järva Tolk &amp; Översättningsservice AB\r\n\t\t\t\t</cbc:RegistrationName>\r\n\t\t\t\t<cac:CompanyID>556560-0854</cac:CompanyID>\r\n\t\t\t\t<cbc:ExemptionReason>Godkänd för F-skatt</cbc:ExemptionReason>\r\n\t\t\t\t<cac:RegistrationAddress/>\r\n\t\t\t\t<cac:TaxScheme>\r\n\t\t\t\t\t<cac:ID>SWT</cac:ID>\r\n\t\t\t\t</cac:TaxScheme>\r\n\t\t\t</cac:PartyTaxScheme>\r\n\t\t\t<cac:Contact>\r\n\t\t\t\t<cbc:Name>Ser</cbc:Name>\r\n\t\t\t\t<cbc:Telephone>08</cbc:Telephone>\r\n\t\t\t\t<cbc:Telefax>084</cbc:Telefax>\r\n\t\t\t\t<cbc:ElectronicMail>mail@mail.se</cbc:ElectronicMail>\r\n\t\t\t</cac:Contact>\r\n\t\t</cac:Party>\r\n\t</cac:SellerParty>\r\n\t<cac:Delivery>\r\n\t\t<cac:DeliveryAddress>\r\n\t\t\t<cbc:StreetName>Hälsingegatan 38</cbc:StreetName>\r\n\t\t\t<cbc:Department>Arbetsförmedlingen HK</cbc:Department>\r\n\t\t\t<cbc:CityName>STOCKHOLM</cbc:CityName>\r\n\t\t\t<cbc:PostalZone>11343</cbc:PostalZone>\r\n\t\t</cac:DeliveryAddress>\r\n\t</cac:Delivery>\r\n\t<cac:PaymentMeans>\r\n\t\t<cac:PaymentMeansTypeCode>1</cac:PaymentMeansTypeCode>\r\n\t\t<cbc:DuePaymentDate>2020-03-15</cbc:DuePaymentDate>\r\n\t\t<cac:PayeeFinancialAccount>\r\n\t\t\t<cac:ID>1250000000052871023751</cac:ID>\r\n\t\t\t<cac:FinancialInstitutionBranch>\r\n\t\t\t\t<cac:FinancialInstitution>\r\n\t\t\t\t\t<cac:ID>ESSESESS</cac:ID>\r\n\t\t\t\t</cac:FinancialInstitution>\r\n\t\t\t</cac:FinancialInstitutionBranch>\r\n\t\t</cac:PayeeFinancialAccount>\r\n\t</cac:PaymentMeans>\r\n\t<cac:PaymentMeans>\r\n\t\t<cac:PaymentMeansTypeCode>1</cac:PaymentMeansTypeCode>\r\n\t\t<cbc:DuePaymentDate>2020-03-15</cbc:DuePaymentDate>\r\n\t\t<cac:PayeeFinancialAccount>\r\n\t\t\t<cac:ID>7990559</cac:ID>\r\n\t\t\t<cac:FinancialInstitutionBranch>\r\n\t\t\t\t<cac:FinancialInstitution>\r\n\t\t\t\t\t<cac:ID>BGABSESS</cac:ID>\r\n\t\t\t\t</cac:FinancialInstitution>\r\n\t\t\t</cac:FinancialInstitutionBranch>\r\n\t\t\t<cac:PaymentInstructionID>5377270</cac:PaymentInstructionID>\r\n\t\t</cac:PayeeFinancialAccount>\r\n\t</cac:PaymentMeans>\r\n\t<cac:PaymentTerms>\r\n\t\t<cbc:Note>30 dagar</cbc:Note>\r\n\t\t<cbc:PenaltySurchargePercent>10</cbc:PenaltySurchargePercent>\r\n\t</cac:PaymentTerms>\r\n\t<cac:TaxTotal>\r\n\t\t<cbc:TotalTaxAmount amountCurrencyID=\"SEK\">12.50\r\n\t\t</cbc:TotalTaxAmount>\r\n\t\t<cac:TaxSubTotal>\r\n\t\t\t<cbc:TaxableAmount amountCurrencyID=\"SEK\">50.00\r\n\t\t\t</cbc:TaxableAmount>\r\n\t\t\t<cbc:TaxAmount amountCurrencyID=\"SEK\">12.50</cbc:TaxAmount>\r\n\t\t\t<cac:TaxCategory>\r\n\t\t\t\t<cac:ID>S</cac:ID>\r\n\t\t\t\t<cbc:Percent>25</cbc:Percent>\r\n\t\t\t\t<cac:TaxScheme>\r\n\t\t\t\t\t<cac:ID>VAT</cac:ID>\r\n\t\t\t\t</cac:TaxScheme>\r\n\t\t\t</cac:TaxCategory>\r\n\t\t</cac:TaxSubTotal>\r\n\t</cac:TaxTotal>\r\n\t<cac:LegalTotal>\r\n\t\t<cbc:LineExtensionTotalAmount amountCurrencyID=\"SEK\">50.00</cbc:LineExtensionTotalAmount>\r\n\t\t<cbc:TaxExclusiveTotalAmount amountCurrencyID=\"SEK\">50.00</cbc:TaxExclusiveTotalAmount>\r\n\t\t<cbc:TaxInclusiveTotalAmount amountCurrencyID=\"SEK\">62.50</cbc:TaxInclusiveTotalAmount>\r\n\t\t<cac:RoundOffAmount amountCurrencyID=\"SEK\">0\r\n\t\t</cac:RoundOffAmount>\r\n\t</cac:LegalTotal>\r\n\t<cac:InvoiceLine>\r\n\t\t<cac:ID>0</cac:ID>\r\n\t\t<cbc:InvoicedQuantity quantityUnitCode=\"st\">1.00\r\n\t\t</cbc:InvoicedQuantity>\r\n\t\t<cbc:LineExtensionAmount amountCurrencyID=\"SEK\">50.00</cbc:LineExtensionAmount>\r\n\t\t<cac:OrderLineReference>\r\n\t\t\t<cac:OrderReference>\r\n\t\t\t\t<cac:BuyersID>3215</cac:BuyersID>\r\n\t\t\t</cac:OrderReference>\r\n\t\t</cac:OrderLineReference>\r\n\t\t<cac:Item>\r\n\t\t\t<cbc:Description>Förmedlingsavgift Godkänd Platstolk\r\n\t\t\t</cbc:Description>\r\n\t\t\t<cac:SellersItemIdentification>\r\n\t\t\t\t<cac:ID>51</cac:ID>\r\n\t\t\t</cac:SellersItemIdentification>\r\n\t\t\t<cac:TaxCategory>\r\n\t\t\t\t<cac:ID>S</cac:ID>\r\n\t\t\t\t<cbc:Percent>25</cbc:Percent>\r\n\t\t\t\t<cac:TaxScheme>\r\n\t\t\t\t\t<cac:ID>VAT</cac:ID>\r\n\t\t\t\t</cac:TaxScheme>\r\n\t\t\t</cac:TaxCategory>\r\n\t\t\t<cac:BasePrice>\r\n\t\t\t\t<cbc:PriceAmount amountCurrencyID=\"SEK\">50.00\r\n\t\t\t\t</cbc:PriceAmount>\r\n\t\t\t</cac:BasePrice>\r\n\t\t</cac:Item>\r\n\t</cac:InvoiceLine>\r\n\t<RequisitionistDocumentReference>\r\n\t\t<cac:ID>LT05Kst: 30374</cac:ID>\r\n\t</RequisitionistDocumentReference>\r\n</Invoice>"
        }
        return valid_response(response)
