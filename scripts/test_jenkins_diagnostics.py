from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import runpy
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, patch

import jenkins_diagnostics as diagnostic

NAME = 'jenkins-proof-aaaaaaaaaaaa-controller-0'
SECRET = 'PRIVATE_PASSWORD_AND_COOKIE'


class JenkinsDiagnosticsTests(unittest.TestCase):
    def observer(self, state=None, logs=None, names=None, probe=None):
        state = state or {'Status': 'running', 'Running': True, 'OOMKilled': False, 'ExitCode': 0,
                          'Error': SECRET, 'Health': {'Log': [SECRET]}}
        def run(command, **kwargs):
            self.assertEqual(command[0], 'docker')
            self.assertEqual(kwargs, {'capture_output': True, 'text': True, 'timeout': 2})
            method = command[1]
            if method == 'ps': text = '\n'.join(names or [NAME, 'production-controller', NAME + SECRET])
            elif method == 'inspect': text = json.dumps({'state': state, 'ports': {}})
            elif method == 'logs': text = logs or 'Started initialization\n' + SECRET
            else: self.fail('Mutation or unexpected Docker read')
            return SimpleNamespace(returncode=0, stdout=text, stderr=SECRET)
        return diagnostic.Diagnostics(run=run, probe=probe or (lambda _: {'status': 503, 'jenkinsHeaderPresent': True}))

    def test_only_allowlisted_docker_state_and_log_flags_are_serialized(self):
        observer = self.observer(logs='Completed initialization\nJenkins is fully up and running\n' + SECRET)
        observer.capture()
        result = observer.report()
        self.assertEqual(list(result['containers']), [NAME])
        state = result['containers'][NAME][-1]['state']
        self.assertTrue(state['logMilestones']['initializationCompleted'])
        self.assertTrue(state['logMilestones']['fullyRunning'])
        self.assertNotIn('Health', state)
        self.assertNotIn('Error', state)
        self.assertNotIn(SECRET, json.dumps(result))

    def test_missing_milestones_are_absent_from_sample_not_a_root_cause(self):
        observer = self.observer()
        observer.capture()
        state = observer.report()['containers'][NAME][-1]['state']
        self.assertFalse(state['logMilestones']['fullyRunning'])
        self.assertIn('not an alternative readiness check', observer.report()['basis'])

    def test_existing_controllers_are_excluded_and_histories_are_bounded(self):
        names = [f'jenkins-proof-{index:012x}-controller-0' for index in range(12)]
        observer = self.observer(names=names)
        observer.ignored = {names[0]}
        for index in range(12):
            observer.probe = lambda _, index=index: {'status': 500 + index}
            observer.capture()
        result = observer.report()['containers']
        self.assertEqual(len(result), 8)
        self.assertNotIn(names[0], result)
        self.assertTrue(all(len(history) == 8 for history in result.values()))
        frozen = deepcopy(result)
        observer.capture()
        self.assertEqual(observer.report()['containers'], frozen)
        result.clear()
        self.assertEqual(len(observer.report()['containers']), 8)

    def test_docker_failures_do_not_expose_stderr_or_exception_text(self):
        for run in (Mock(side_effect=RuntimeError(SECRET)), Mock(return_value=SimpleNamespace(returncode=1, stdout=SECRET, stderr=SECRET))):
            observer = diagnostic.Diagnostics(run=run)
            observer.capture()
            self.assertEqual(observer.report()['containers'], {})
            self.assertEqual(observer.report()['errors'], {'dockerReadFailed': 1})
            self.assertNotIn(SECRET, json.dumps(observer.report()))

    def test_bad_inspect_fields_never_escape_the_allowlist(self):
        observer = self.observer(state={'Status': SECRET, 'Running': SECRET, 'OOMKilled': SECRET, 'ExitCode': SECRET})
        observer.capture()
        self.assertNotIn(SECRET, json.dumps(observer.report()))
        observer = self.observer(probe=Mock(side_effect=RuntimeError(SECRET)))
        observer.capture()
        self.assertEqual(observer.report()['errors'], {'observationUnavailable': 1})
        self.assertNotIn(SECRET, json.dumps(observer.report()))

    def test_probe_only_connects_to_numeric_loopback_and_never_follows_redirects(self):
        for bindings in [[{'HostIp': '0.0.0.0', 'HostPort': '8080'}], [{'HostIp': '127.0.0.1', 'HostPort': 'http://outside.example'}], [{'HostIp': '127.0.0.1', 'HostPort': '65536'}], []]:
            with patch.object(diagnostic.http.client, 'HTTPConnection') as connection:
                self.assertEqual(diagnostic.loopback_http({'8080/tcp': bindings}), {'observation': 'no-loopback-binding'})
                connection.assert_not_called()
        connection = Mock(); response = connection.getresponse.return_value
        response.status = 302; response.getheader.return_value = SECRET
        with patch.object(diagnostic.http.client, 'HTTPConnection', return_value=connection) as constructor:
            result = diagnostic.loopback_http({'8080/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '49152'}]})
            constructor.assert_called_once_with('127.0.0.1', 49152, timeout=1)
        connection.request.assert_called_once_with('GET', '/login')
        connection.close.assert_called_once()
        response.read.assert_not_called()
        self.assertEqual(result, {'status': 302, 'jenkinsHeaderPresent': True})
        self.assertNotIn(SECRET, json.dumps(result))

    def test_probe_connection_errors_are_sanitized_and_closed(self):
        connection = Mock(); connection.request.side_effect = RuntimeError(SECRET)
        with patch.object(diagnostic.http.client, 'HTTPConnection', return_value=connection):
            result = diagnostic.loopback_http({'8080/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '49152'}]})
        self.assertEqual(result, {'observation': 'connection-unavailable'})
        connection.close.assert_called_once()

    def test_observer_lifecycle_stops_when_the_example_exits_or_raises(self):
        for error in (None, RuntimeError('example failed')):
            observer = self.observer()
            sampled = threading.Event()
            with patch.object(observer, 'capture', side_effect=sampled.set) as capture:
                try:
                    with observer:
                        self.assertTrue(sampled.wait(1))
                        if error: raise error
                except RuntimeError as caught:
                    self.assertIs(caught, error)
            self.assertTrue(observer.stop.is_set())
            self.assertFalse(observer.thread.is_alive())
            capture.assert_called()

    def test_run_example_preserves_command_environment_timeout_and_failure_result(self):
        for result in (SimpleNamespace(returncode=1, stdout='', stderr=SECRET), TimeoutError('example timeout')):
            observer = MagicMock(); observer.report.return_value = {'containers': {}, 'errors': {}}
            run = Mock(side_effect=result) if isinstance(result, Exception) else Mock(return_value=result)
            output = io.StringIO()
            with redirect_stdout(output):
                try:
                    actual = diagnostic.run_example(['python', 'example.py'], {'TOKEN': SECRET}, run, lambda: observer)
                    self.assertIs(actual, result)
                except TimeoutError as caught:
                    self.assertIs(caught, result)
            run.assert_called_once_with(['python', 'example.py'], capture_output=True, text=True, timeout=600, env={'TOKEN': SECRET})
            observer.__enter__.assert_called_once()
            observer.__exit__.assert_called_once()
            self.assertIn('jenkinsDiagnostics', json.loads(output.getvalue()))
            self.assertNotIn(SECRET, output.getvalue())

    def test_article_checker_rejects_failed_example_without_dumping_stderr(self):
        result = SimpleNamespace(returncode=1, stdout='', stderr='Jenkins login was not ready within 180 seconds\n' + SECRET)
        with patch.object(diagnostic, 'run_example', return_value=result), redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError) as error:
                runpy.run_path('scripts/check_jenkins_examples.py')
        self.assertIn('readiness deadline exceeded', str(error.exception))
        self.assertNotIn(SECRET, str(error.exception))


if __name__ == '__main__': unittest.main()
