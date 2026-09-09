import contextlib
import io
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import requests
from rich._emoji_codes import EMOJI


PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get('GEOWIFI_SCRIPT', PROJECT_DIR / 'geowifi.py'))
REMOVED_EMOJI = ['cd', 'ab', 'ox', 'wc', 'cl', 'id', 'sa', 'vs', 'o2', 'on', 'tm']


class FakeResponse:
    status_code = 200
    content = b'\0' * 10
    text = 'Test Vendor'

    def __init__(self, url):
        self.url = url

    def json(self):
        if 'wigle.net' in self.url:
            return {'success': False, 'message': 'API key required'}
        if 'mylnikov.org' in self.url:
            return {'result': 404, 'desc': 'Object was not found'}
        if 'googleapis.com' in self.url or 'combain.com' in self.url:
            return {'error': {'message': 'API key required'}}
        if 'wifidb.net' in self.url:
            return {'features': []}
        if 'openwifimap.net' in self.url:
            return {'rows': []}
        if 'freifunk-karte.de' in self.url:
            return {'allTheRouters': []}
        return {}

    def raise_for_status(self):
        return None


class RequestTimeoutTests(unittest.TestCase):
    def run_cli(self, arguments):
        calls = []
        emoji_values = {name: EMOJI[name] for name in REMOVED_EMOJI}

        def request(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse(url)

        with tempfile.TemporaryDirectory() as temporary_directory:
            Path(temporary_directory, 'results').mkdir()
            previous_cwd = os.getcwd()
            previous_argv = sys.argv
            os.chdir(temporary_directory)
            sys.argv = [str(SCRIPT), *arguments]
            try:
                with mock.patch('requests.get', side_effect=request), \
                        mock.patch('requests.post', side_effect=request), \
                        contextlib.redirect_stdout(io.StringIO()):
                    namespace = runpy.run_path(str(SCRIPT), run_name='__main__')
                return calls, namespace
            finally:
                EMOJI.update(emoji_values)
                sys.argv = previous_argv
                os.chdir(previous_cwd)

    def test_all_provider_requests_use_the_shared_timeout(self):
        bssid_calls, _ = self.run_cli(
            ['-s', 'bssid', '-o', 'json', '00:23:CD:12:34:56']
        )
        ssid_calls, _ = self.run_cli(['-s', 'ssid', '-o', 'json', 'test-network'])
        calls = bssid_calls + ssid_calls

        self.assertEqual(11, len(calls))
        self.assertTrue(all(call[1]['timeout'] == 20 for call in calls))

    def test_apple_timeout_is_returned_as_a_provider_error(self):
        _, namespace = self.run_cli(
            ['-s', 'bssid', '-o', 'json', '00:23:CD:12:34:56']
        )

        with mock.patch('requests.post', side_effect=requests.Timeout('request timed out')):
            result = namespace['apple_bssid']('00:23:CD:12:34:56')

        self.assertEqual({'module': 'apple', 'error': 'request timed out'}, result)


if __name__ == '__main__':
    unittest.main()
