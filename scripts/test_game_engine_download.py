from contextlib import nullcontext
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError
from types import SimpleNamespace
import check_game_engine_example as checker


class GameEngineDownloadTests(TestCase):
    url = 'https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/' + checker.ASSET

    def response(self, payload):
        return nullcontext(SimpleNamespace(read=lambda: payload))

    def test_gateway_error_retries_same_release_asset_once(self):
        failure = HTTPError(self.url, 504, 'Gateway timeout', {}, None)
        with patch.object(checker, 'urlopen', side_effect=[failure, self.response(b'archive')]) as get:
            self.assertEqual(checker.download_runtime(self.url), b'archive')
            self.assertEqual([call.args[0] for call in get.call_args_list], [self.url, self.url + '?download=1'])

    def test_missing_asset_does_not_fall_back_to_another_release(self):
        failure = HTTPError(self.url, 404, 'Not found', {}, None)
        with patch.object(checker, 'urlopen', side_effect=failure) as get:
            with self.assertRaises(HTTPError): checker.download_runtime(self.url)
            self.assertEqual(get.call_count, 1)

    def test_second_failure_stops_instead_of_looping(self):
        failure = HTTPError(self.url, 504, 'Gateway timeout', {}, None)
        with patch.object(checker, 'urlopen', side_effect=failure) as get:
            with self.assertRaises(HTTPError): checker.download_runtime(self.url)
            self.assertEqual(get.call_count, 2)

    def test_retry_bytes_must_still_match_pinned_archive_checksum(self):
        with patch('sys.argv', ['check_game_engine_example.py', '--download']), \
             patch.object(checker, 'example', return_value=('project', 'script', 'command', 'output')), \
             patch.object(checker, 'download_runtime', return_value=b'wrong archive'), \
             patch.object(checker, 'execute', side_effect=AssertionError('Unverified bytes must not execute')):
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'): checker.main()
