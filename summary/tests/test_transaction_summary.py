# from django.test import TestCase
import json
import pandas as pd
import datetime
import requests
from django.test import Client
from unittest import TestCase, mock


class TestTransactionSummaryView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        # patch `utils.utils.transaction_files`
        self.transaction_files_patch = mock.patch("utils.utils.transaction_files")
        self.mock_files_patcher = self.transaction_files_patch.start()
        self.mock_files_patcher.return_value = []

        # Dummy data
        self.dummy_data = {
            "transactionId": [1, 2, 3, 4, 5],
            "productId": [10, 11, 10, 12, 13],
            "transactionAmount": [10, 20, 30, 20, 5],
            "transactionDatetime": [
                self.replace_time_stamp(datetime.datetime.now()),
                self.replace_time_stamp(datetime.datetime.now() - datetime.timedelta(days=1)),
                self.replace_time_stamp(datetime.datetime.now() - datetime.timedelta(days=5)),
                self.replace_time_stamp(datetime.datetime.now() - datetime.timedelta(days=3)),
                self.replace_time_stamp(datetime.datetime.now() - datetime.timedelta(days=5))
            ],
            "productName": ["P1", "P2", "P3", "P1", "P2"],
            "productManufacturingCity": ["C1", "C2", "C3", "C2", "C1"]
        }

        self.mock_data = {"transaction_data": pd.DataFrame(data=self.dummy_data)}

    def tearDown(self) -> None:
        self.mock_files_patcher.stop()

    @staticmethod
    def replace_time_stamp(data):
        """To avoid timestamp, replace hour, minute, second and microsecond to 0"""
        return data.replace(hour=0, minute=0, second=0, microsecond=0)

    # ------------------------------------------------------------------------------- #
    # -------------------- Transaction Summary test cases --------------------------- #
    # ------------------------------------------------------------------------------- #

    def test_transaction_summary(self):
        # Test transaction summary by transaction id
        expected = {
            'summary': [
                {
                    'transactionId': 2,
                    'productName': 'P2',
                    'transactionAmount': 20,
                    'transactionDatetime': self.replace_time_stamp(
                        datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }

        # test for transaction id 2
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummary/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

        # test for transaction id 5
        expected = {
            'summary': [
                {
                    'transactionId': 5,
                    'productName': 'P2',
                    'transactionAmount': 5,
                    'transactionDatetime': self.replace_time_stamp(
                        datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummary/5/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_with_invalid_transaction_id(self):
        # Test transaction summary with invalid transaction id
        expected = {'summary': 'No records found'}
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummary/20/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_with_empty_data(self):
        # Test transaction summary by transaction id, with empty data
        empty_data = {"transaction_data": pd.DataFrame(columns=list(self.dummy_data.keys()))}
        expected = {'summary': 'No records found'}
        # test for last 2 days
        with mock.patch("summary.views.DATA", empty_data):
            response = self.client.get("/transaction/transactionSummary/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_404(self):
        # Test transaction summary by transaction id, with invalid url
        response = self.client.get("/transaction/transactionSummaryByProducts/abc/")
        self.assertEqual(requests.codes.not_found, response.status_code)

        response = self.client.get("/transaction/transactionSummaryByProducts/abc12/")
        self.assertEqual(requests.codes.not_found, response.status_code)

    # ------------------------------------------------------------------------------- #
    # -------------- Transaction Summary by Product test cases ---------------------- #
    # ------------------------------------------------------------------------------- #

    def test_transaction_summary_by_product(self):
        # Test transaction summary by product
        expected = {
            "summary": [
                {"productName": "P1", "totalAmount": 10},
                {"productName": "P2", "totalAmount": 20}
            ]
        }

        # test for last 2 days
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummaryByProducts/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

        # test for last 10 days
        expected = {
            'summary': [
                {'productName': 'P1', 'totalAmount': 30},
                {'productName': 'P2', 'totalAmount': 25},
                {'productName': 'P3', 'totalAmount': 30}
            ]
        }
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummaryByProducts/10/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_by_product_with_empty_data(self):
        # Test transaction summary by product, with empty data
        empty_data = {"transaction_data": pd.DataFrame(columns=list(self.dummy_data.keys()))}
        expected = {"summary": "No records found"}
        # test for last 2 days
        with mock.patch("summary.views.DATA", empty_data):
            response = self.client.get("/transaction/transactionSummaryByProducts/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_by_product_404(self):
        # Test transaction summary by product, with invalid url
        response = self.client.get("/transaction/transactionSummaryByProducts/abc/")
        self.assertEqual(requests.codes.not_found, response.status_code)

        response = self.client.get("/transaction/transactionSummaryByProducts/abc12/")
        self.assertEqual(requests.codes.not_found, response.status_code)

    # ------------------------------------------------------------------------------- #
    # -------------- Transaction Summary by Product test cases ---------------------- #
    # ------------------------------------------------------------------------------- #

    def test_transaction_summary_by_manufacturing_city(self):
        # Test transaction summary by product manufacturing city
        expected = {
            'summary': [
                {'cityName': 'C1', 'totalAmount': 10},
                {'cityName': 'C2', 'totalAmount': 20}
            ]
        }

        # test for last 2 days
        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummaryByManufacturingCity/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

        # test for last 10 days
        expected = {
            'summary': [
                {'cityName': 'C1', 'totalAmount': 15},
                {'cityName': 'C2', 'totalAmount': 40},
                {'cityName': 'C3', 'totalAmount': 30}
            ]
        }

        with mock.patch("summary.views.DATA", self.mock_data):
            response = self.client.get("/transaction/transactionSummaryByManufacturingCity/10/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    def test_transaction_summary_by_manufacturing_city_404(self):
        # Test transaction summary by product manufacturing city, with invalid url
        response = self.client.get("/transaction/transactionSummaryByManufacturingCity/abc/")
        self.assertEqual(requests.codes.not_found, response.status_code)

        response = self.client.get("/transaction/transactionSummaryByManufacturingCity/abc12/")
        self.assertEqual(requests.codes.not_found, response.status_code)

    def test_transaction_summary_by_manufacturing_city_with_empty_data(self):
        # Test transaction summary by product, with empty data
        empty_data = {"transaction_data": pd.DataFrame(columns=list(self.dummy_data.keys()))}
        expected = {"summary": "No records found"}
        # test for last 2 days
        with mock.patch("summary.views.DATA", empty_data):
            response = self.client.get("/transaction/transactionSummaryByManufacturingCity/2/")
            self.assertEqual(requests.codes.ok, response.status_code)
            actual = json.loads(response.content)
            self.assertDictEqual(expected, actual)

    # ------------------------------------------------------------------------------- #
    # ---------------------- Test cases for Data Load API --------------------------- #
    # ------------------------------------------------------------------------------- #

    def test_load_data_with_response_ok(self):
        # Test case for url pattern `/transaction/load_data/`
        self.client.get = mock.Mock(return_value=requests.Response())
        self.client.get.return_value.status_code = 200

        response = self.client.get("/transaction/load_data/")

        self.assertEqual(requests.codes.ok, response.status_code)

    def test_load_data_with_server_error(self):
        # Test case for url pattern `/transaction/load_data/` for server error
        self.client.get = mock.Mock(return_value=requests.Response())

        self.client.get.return_value.status_code = 500
        response = self.client.get("/transaction/load_data/")
        self.assertEqual(requests.codes.internal_server_error, response.status_code)

        self.client.get.return_value.status_code = 503
        response = self.client.get("/transaction/load_data/")
        self.assertEqual(requests.codes.service_unavailable, response.status_code)

        self.client.get.return_value.status_code = 504
        response = self.client.get("/transaction/load_data/")
        self.assertEqual(requests.codes.gateway_timeout, response.status_code)

        self.client.get.return_value.status_code = 502
        response = self.client.get("/transaction/load_data/")
        self.assertEqual(requests.codes.bad_gateway, response.status_code)
