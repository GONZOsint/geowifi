import contextlib
import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        return {}

    def raise_for_status(self):
        return None


class OutputTests(unittest.TestCase):
    def run_cli(self, arguments):
        emoji_values = {name: EMOJI[name] for name in REMOVED_EMOJI}

        def request(url, **kwargs):
            return FakeResponse(url)

        with tempfile.TemporaryDirectory() as temporary_directory:
            previous_cwd = os.getcwd()
            previous_argv = sys.argv
            os.chdir(temporary_directory)
            sys.argv = [str(SCRIPT), *arguments]
            try:
                with mock.patch('requests.get', side_effect=request), \
                        mock.patch('requests.post', side_effect=request), \
                        contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(SCRIPT), run_name='__main__')
                output_files = list(Path(temporary_directory, 'results').iterdir())
                return output_files[0].suffix, output_files[0].read_text()
            finally:
                EMOJI.update(emoji_values)
                sys.argv = previous_argv
                os.chdir(previous_cwd)

    def test_json_export_creates_results_directory(self):
        suffix, contents = self.run_cli(
            ['-s', 'bssid', '-o', 'json', '00:23:CD:12:34:56']
        )

        self.assertEqual('.json', suffix)
        self.assertIsInstance(json.loads(contents), list)

    def test_default_output_creates_non_empty_map(self):
        suffix, contents = self.run_cli(['-s', 'bssid', '00:23:CD:12:34:56'])

        self.assertEqual('.html', suffix)
        self.assertIn('<!DOCTYPE html>', contents)

    def test_help_does_not_create_results_directory(self):
        self.assert_clean_exit_creates_no_results(['--help'], expected_exit_code=0)

    def test_invalid_bssid_does_not_create_results_directory(self):
        self.assert_clean_exit_creates_no_results(
            ['-s', 'bssid', 'not-a-bssid'], expected_exit_code=1
        )

    def assert_clean_exit_creates_no_results(self, arguments, expected_exit_code):
        emoji_values = {name: EMOJI[name] for name in REMOVED_EMOJI}
        with tempfile.TemporaryDirectory() as temporary_directory:
            previous_cwd = os.getcwd()
            previous_argv = sys.argv
            os.chdir(temporary_directory)
            sys.argv = [str(SCRIPT), *arguments]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as exit_context:
                        runpy.run_path(str(SCRIPT), run_name='__main__')
                self.assertEqual(expected_exit_code, exit_context.exception.code)
                self.assertFalse(Path(temporary_directory, 'results').exists())
            finally:
                EMOJI.update(emoji_values)
                sys.argv = previous_argv
                os.chdir(previous_cwd)


if __name__ == '__main__':
    unittest.main()
