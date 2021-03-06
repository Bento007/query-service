import unittest
from unittest.mock import Mock, patch

# from lambdas.load_data.load_data import extract_transform_load
# from load_data_lambda.app import load_data


@unittest.skip("WIP")
class TestLoadData(unittest.TestCase):

    @patch('load_data_lambda.app.extract_transform_load')
    @patch('load_data_lambda.app.extractor', 'foo')
    @patch('load_data_lambda.app.loader', 'bah')
    def test_query_service_load_data(self, mock_etl):

        '''
        mock_event_data = {"Records": [{'messageId': '33b4de0b-274a-48f0-9b5c-ee600b439c6c',
                                        'receiptHandle': 'AQEBm6V306aUkJhPlCT2hcBz9Q1QXmNmqPV4UC/ebmGQYAMLKQoHxn2k',
                                        'body': '{"bundle_uuid": "9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c", '
                                                '"bundle_version": "2018-11-27T211302.714868Z"}',
                                        'attributes': {'ApproximateReceiveCount': '1',
                                                       'SentTimestamp': '1543357453729',
                                                       'SenderId': 'AROAIW2WQHOU5B2TZ546I:query-api-dev',
                                                       'ApproximateFirstReceiveTimestamp': '1543357453745'},
                                        'messageAttributes': {}, 'md5OfBody': '4bcabebd5f583eb0b964841edbf3a3ca',
                                        'eventSource': 'aws:sqs',
                                        'eventSourceARN': 'arn:aws:sqs:us-east-1:*:dcp-query-data-input-queue-',
                                        'awsRegion': 'us-east-1'}]}
        '''
        # load_data(mock_event_data, 'context')
        mock_etl.assert_called_once_with(
            extractor='foo',
            loader='bah',
            bundle_uuid='9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c',
            bundle_version='2018-11-27T211302.714868Z'
        )

    @patch('query.lambdas.load_data.load_data.BundleDocumentTransform.transform')
    def test_extract_transform_load(self, mock_transform):
        mock_transform.return_value = 'TRANSFORMED BUNDLE'
        extractor = Mock()
        loader = Mock()
        extractor.extract_bundle.return_value = 'BUNDLE'
        # extract_transform_load(extractor, loader, 'UUID', 'VERSION')
        extractor.extract_bundle.assert_called_once_with('UUID', 'VERSION')
        mock_transform.assert_called_once_with('BUNDLE')
        loader.load.assert_called_once_with('BUNDLE', 'TRANSFORMED BUNDLE')
