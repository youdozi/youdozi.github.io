import contextlib
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import search_console as sc


class SearchConsoleTests(unittest.TestCase):
    def test_submit_checks_property_then_puts_and_reads_encoded_sitemap(self):
        with patch.object(sc, 'api', side_effect=[{'permissionLevel': 'siteOwner'}, {}, {'isPending': True}]) as api:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                sc.execute('private-token')
        calls = api.call_args_list
        self.assertEqual([call.args[1] for call in calls], ['GET', 'PUT', 'GET'])
        self.assertEqual(calls[1].args[2], 'sites/https%3A%2F%2Fyoudozi.github.io%2F/sitemaps/https%3A%2F%2Fyoudozi.github.io%2Fsitemap.xml')
        self.assertNotIn('private-token', output.getvalue())
        self.assertIn('사이트맵 제출 성공', output.getvalue())

    def test_status_never_submits(self):
        with patch.object(sc, 'api', side_effect=[{}, {}]) as api:
            with contextlib.redirect_stdout(io.StringIO()):
                sc.execute('token', status_only=True)
        self.assertEqual([call.args[1] for call in api.call_args_list], ['GET', 'GET'])

    def test_property_access_failure_prevents_submission(self):
        with patch.object(sc, 'api', side_effect=RuntimeError('denied')) as api:
            with self.assertRaises(RuntimeError):
                sc.execute('token')
        self.assertEqual(api.call_count, 1)

    def test_api_403_is_actionable_and_does_not_leak_response(self):
        import sys
        from types import SimpleNamespace
        # Isolate transport; the test suite needs no Google dependencies.
        with patch.dict(sys.modules, {'certifi': SimpleNamespace(where=lambda: None)}):
            with patch.object(sc, 'urlopen', side_effect=HTTPError('url', 403, 'sensitive', {}, None)):
                with self.assertRaisesRegex(RuntimeError, 'HTTP 403') as error:
                    sc.api('private-token', 'PUT', 'sites/example')
        self.assertNotIn('private-token', str(error.exception))
        self.assertNotIn('sensitive', str(error.exception))

    def test_token_cache_is_private_including_after_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'token.json'
            path.write_text('{}')
            path.chmod(0o644)
            sc.private_json(path, {'refresh_token': 'private'})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(json.loads(path.read_text())['refresh_token'], 'private')
            self.assertEqual(list(Path(folder).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
