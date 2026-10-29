"""Bounded, read-only observations of disposable Jenkins labs; never emit raw logs."""
from collections import Counter
from copy import deepcopy
import http.client
import json
import re
import subprocess
import threading
import time

NAME = re.compile(r'jenkins-proof-[a-f0-9]{12}-controller-[0-9]+')
MILESTONES = {
    'initializationStarted': 'Started initialization',
    'initializationCompleted': 'Completed initialization',
    'fullyRunning': 'Jenkins is fully up and running',
    'setupRequired': 'Jenkins initial setup is required',
    'outOfMemoryReported': 'OutOfMemoryError',
    'dnsFailureReported': 'UnknownHostException',
}


def loopback_http(ports):
    bindings = ports.get('8080/tcp') or []
    for binding in bindings:
        port = binding.get('HostPort', '')
        if binding.get('HostIp') != '127.0.0.1' or not re.fullmatch(r'[0-9]{1,5}', port):
            continue
        if not 1 <= int(port) <= 65535:
            continue
        connection = http.client.HTTPConnection('127.0.0.1', int(port), timeout=1)
        try:
            connection.request('GET', '/login')
            response = connection.getresponse()
            return {'status': response.status, 'jenkinsHeaderPresent': bool(response.getheader('X-Jenkins'))}
        except Exception:
            return {'observation': 'connection-unavailable'}
        finally:
            connection.close()
    return {'observation': 'no-loopback-binding'}


class Diagnostics:
    """Watch newly appearing lab controllers on this daemon, not pre-existing ones.

    The CI runner is dedicated to this job. Concurrent locally started labs with
    the same naming convention can also appear. No containers are changed.
    """
    def __init__(self, run=subprocess.run, probe=loopback_http):
        self.run, self.probe = run, probe
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.states, self.errors = {}, Counter()
        self.ignored = set()
        self.started = time.monotonic()
        self.thread = None

    def read(self, *args):
        try:
            result = self.run(['docker', *args], capture_output=True, text=True, timeout=2)
            if result.returncode:
                raise ValueError('read failed')
            return result.stdout, result.stderr
        except Exception:
            with self.lock:
                self.errors['dockerReadFailed'] += 1
            return None

    def names(self):
        result = self.read('ps', '-a', '--filter', 'name=jenkins-proof-', '--format', '{{.Names}}')
        return {n for n in result[0].splitlines() if NAME.fullmatch(n)} if result else set()

    def capture(self):
        for name in sorted(self.names() - self.ignored):
            if self.stop.is_set(): return
            if name not in self.states and len(self.states) >= 8: continue
            raw = self.read('inspect', '--format', '{"state":{{json .State}},"ports":{{json .NetworkSettings.Ports}}}', name)
            if raw is None: continue
            try:
                data = json.loads(raw[0]); state = data['state']
                item = {key: state.get(key) for key in ('Running', 'OOMKilled', 'ExitCode')
                        if type(state.get(key)) is (int if key == 'ExitCode' else bool)}
                if state.get('Status') in ('created', 'running', 'paused', 'restarting', 'removing', 'exited', 'dead'):
                    item['status'] = state['Status']
                if self.stop.is_set(): return
                logs = self.read('logs', '--tail', '400', name)
                item['logMilestones'] = ({key: phrase in ''.join(logs) for key, phrase in MILESTONES.items()}
                                         if logs is not None else None)
                if self.stop.is_set(): return
                # Fixed localhost request; redirects, cookies, bodies and headers are never serialized.
                item['http'] = self.probe(data.get('ports') or {})
                with self.lock:
                    history = self.states.setdefault(name, [])
                    if not history or history[-1]['state'] != item:
                        history.append({'elapsedSeconds': round(time.monotonic() - self.started, 1), 'state': item})
                        del history[:-8]
            except Exception:
                with self.lock:
                    self.errors['observationUnavailable'] += 1

    def watch(self):
        while not self.stop.is_set():
            try:
                self.capture()
            except Exception:
                with self.lock:
                    self.errors['observationUnavailable'] += 1
            self.stop.wait(2)

    def __enter__(self):
        self.ignored = self.names()
        self.thread = threading.Thread(target=self.watch, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join(timeout=4)

    def report(self):
        with self.lock:
            return {'basis': 'Sampled diagnostic observations; not an alternative readiness check or root-cause proof.',
                    'containers': deepcopy(self.states), 'errors': dict(self.errors)}


def run_example(command, env, run=subprocess.run, diagnostics=Diagnostics):
    observer = diagnostics()
    try:
        with observer:
            return run(command, capture_output=True, text=True, timeout=600, env=env)
    finally:
        print(json.dumps({'jenkinsDiagnostics': observer.report()}), flush=True)
