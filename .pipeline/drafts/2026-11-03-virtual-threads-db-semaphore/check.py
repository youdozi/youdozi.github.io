import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parent
IMAGE = 'postgres@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5'


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, timeout=300, **kwargs)
    if result.returncode:
        print(result.stdout, result.stderr)
        result.check_returncode()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk', type=Path, action='append', required=True)
    parser.add_argument('--gradle', default='gradle')
    args = parser.parse_args()
    name = 'blog-db-semaphore-' + uuid.uuid4().hex[:12]
    created = False
    results = []
    try:
        run(['docker', 'run', '-d', '--rm', '--name', name,
             '--tmpfs', '/var/lib/postgresql/data', '-p', '127.0.0.1::5432',
             '-e', 'POSTGRES_USER=demo', '-e', 'POSTGRES_DB=demo',
             '-e', 'POSTGRES_PASSWORD=example-only', IMAGE])
        created = True
        for _ in range(60):
            ready = subprocess.run(['docker', 'exec', name, 'pg_isready', '-h', '127.0.0.1', '-U', 'demo', '-d', 'demo'], capture_output=True)
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('Temporary PostgreSQL did not become ready')
        port = run(['docker', 'port', name, '5432/tcp']).stdout.strip().split(':')[-1]
        postgres = run(['docker', 'exec', name, 'psql', '-U', 'demo', '-d', 'demo', '-Atc', 'SHOW server_version']).stdout.strip()
        for home in args.jdk:
            home = home.resolve()
            env = dict(os.environ, JAVA_HOME=str(home), DB_URL=f'jdbc:postgresql://127.0.0.1:{port}/demo?connectTimeout=2&socketTimeout=5',
                       DB_USER='demo', DB_PASSWORD='example-only')
            env['PATH'] = str(home / 'bin') + os.pathsep + env.get('PATH', '')
            version = run([str(home / 'bin/java'), '--version']).stdout.strip()
            if not results:
                gradle = run([args.gradle, '--version'], env=env).stdout
                assert re.search(r'Gradle 8\.14\.3(?:\s|$)', gradle), gradle
                run([args.gradle, '--no-daemon', '-q', 'copyDependencies'], cwd=ROOT, env=env)
            classes = ROOT / 'build' / ('jdk-' + str(len(results)))
            classes.mkdir(parents=True, exist_ok=True)
            run([str(home / 'bin/javac'), '--release', '21', '-cp', 'build/deps/*', '-d', str(classes),
                 'DbBulkhead.java', 'Demo.java', 'DbBulkheadChecks.java'], cwd=ROOT, env=env)
            classpath = str(classes) + os.pathsep + 'build/deps/*'
            demo = run([str(home / 'bin/java'), '-cp', classpath, 'Demo'], cwd=ROOT, env=env)
            assert demo.stdout.strip().splitlines() == ['overload=rejected', 'query=42', 'available=1'], demo.stdout
            checks = run([str(home / 'bin/java'), '-cp', classpath, 'DbBulkheadChecks'], cwd=ROOT, env=env)
            assert 'connection-active=0' in checks.stdout and 'available=1,slots=2' in checks.stdout, checks.stdout
            results.append({'jdk': version, 'gradle': re.search(r'^Gradle ([^\s]+)$', gradle, re.M)[1],
                            'demo': demo.stdout.strip().splitlines(), 'contracts': checks.stdout.strip().splitlines()})
        article = ROOT / 'article.ko.md'
        if article.exists():
            body = article.read_text()
            for filename, language in [('DbBulkhead.java', 'java'), ('Demo.java', 'java'), ('build.gradle', 'groovy'), ('settings.gradle', 'groovy')]:
                match = re.search(r'### `' + re.escape(filename) + r'`\n\n```' + language + r'\n(.*?)\n```', body, re.S)
                assert match and match[1] + '\n' == (ROOT / filename).read_text(), filename
        site = ROOT.parents[2]
        published = site / 'src/content/posts/ko/2026-11-03-virtual-threads-db-semaphore.md'
        if published.exists():
            def body(raw):
                return re.sub(r'^---\n[\s\S]*?\n---\n', '', raw, count=1)
            assert body(published.read_text()) == body(article.read_text()).replace(
                '(./db-semaphore-ko.svg)', '(/assets/img/architecture/db-semaphore-ko.svg)')
            assert (site / 'assets/img/architecture/db-semaphore-ko.svg').read_bytes() == (ROOT / 'db-semaphore-ko.svg').read_bytes()
        report = {'observedAt': datetime.now(timezone.utc).isoformat(), 'postgres': postgres, 'image': IMAGE,
                  'results': results, 'scope': 'Real PostgreSQL and HikariCP correctness checks, not a load benchmark',
                  'checks': ['commit', 'SQL rollback', 'runtime exception cleanup', 'bounded admission',
                             'timed wait', 'interrupted wait without permit inflation', 'cancellation with continuing work',
                             'server statement timeout and recovery', 'connection-pool exhaustion', 'repeated failure cleanup'],
                  'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*') if p.suffix in ('.java', '.gradle')}}
        (ROOT / 'execution.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False))
    finally:
        if created:
            run(['docker', 'rm', '-f', name])


if __name__ == '__main__':
    main()
