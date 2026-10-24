#!/usr/bin/env python3
"""Submit this site's sitemap using Google OAuth; never publish credentials."""
import argparse
import json
import os
import ssl
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

SITE = 'https://youdozi.github.io/'
SITEMAP = SITE + 'sitemap.xml'
SCOPE = 'https://www.googleapis.com/auth/webmasters'
CONFIG = Path.home() / '.config' / 'youdozi-search-console'


def private_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.token-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def access_token(args):
    token = os.environ.get('SEARCH_CONSOLE_ACCESS_TOKEN')
    if token:
        return token
    client = args.client or os.environ.get('GOOGLE_OAUTH_CLIENT_FILE')
    if not args.token_file.is_file() and not client:
        raise RuntimeError(
            'Google 인증이 없습니다. 데스크톱 앱 OAuth JSON을 만든 뒤 '
            '--client /절대경로/client.json 으로 실행하세요. '
            '설정 방법: README.md의 Search Console 항목')
    try:
        from google.auth.transport.requests import Request as GoogleRequest
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise RuntimeError('먼저 pip install -r scripts/requirements-search-console.txt 를 실행하세요.') from None
    credentials = None
    if args.token_file.is_file():
        credentials = Credentials.from_authorized_user_file(str(args.token_file), scopes=[SCOPE])
        if not credentials.valid and credentials.refresh_token:
            try:
                credentials.refresh(GoogleRequest())
            except Exception:
                if not client:
                    raise RuntimeError('Google 인증 갱신에 실패했습니다. --client로 다시 로그인하세요.') from None
                credentials = None
    if not credentials or not credentials.valid:
        if not client:
            raise RuntimeError('Google 로그인이 필요합니다. --client로 OAuth JSON 경로를 지정하세요.')
        with open(client) as stream:
            config = json.load(stream)
        installed = config.get('installed', {})
        if (not installed.get('client_id') or
                installed.get('auth_uri') != 'https://accounts.google.com/o/oauth2/auth' or
                installed.get('token_uri') != 'https://oauth2.googleapis.com/token'):
            raise RuntimeError('Google의 데스크톱 앱 유형 OAuth 클라이언트 JSON을 사용하세요.')
        flow = InstalledAppFlow.from_client_config(config, scopes=[SCOPE], autogenerate_code_verifier=True)
        print('브라우저에서 Google 로그인과 Search Console 접근을 승인하세요.', flush=True)
        credentials = flow.run_local_server(
            host='127.0.0.1', port=0, open_browser=True, timeout_seconds=180,
            authorization_prompt_message='인증 브라우저를 열었습니다.',
            success_message='Google 인증을 마쳤습니다. 이 창을 닫아도 됩니다.',
            access_type='offline', prompt='consent')
    private_json(args.token_file, json.loads(credentials.to_json()))
    return credentials.token


def api(token, method, path):
    request = Request('https://www.googleapis.com/webmasters/v3/' + path,
                      headers={'Authorization': 'Bearer ' + token}, method=method)
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=30, context=context) as response:
            body = response.read()
            return json.loads(body) if body else {}
    except HTTPError as error:
        messages = {
            401: 'Google 인증이 만료되었거나 유효하지 않습니다.',
            403: 'Search Console API 활성화, OAuth 범위, 해당 속성의 사용자 권한을 확인하세요.',
            404: 'Search Console에 정확한 URL-prefix 속성과 사이트맵이 등록되어 있는지 확인하세요.',
        }
        raise RuntimeError(f'Google API HTTP {error.code}: ' + messages.get(error.code, '요청에 실패했습니다.')) from None
    except URLError:
        raise RuntimeError('Google API 네트워크 연결 또는 TLS 인증서 검증에 실패했습니다.') from None


def execute(token, status_only=False):
    site_path = 'sites/' + quote(SITE, safe='')
    site = api(token, 'GET', site_path)
    print('Search Console 속성:', site.get('siteUrl', SITE))
    print('접근 권한:', site.get('permissionLevel', 'unknown'))
    sitemap_path = site_path + '/sitemaps/' + quote(SITEMAP, safe='')
    if not status_only:
        api(token, 'PUT', sitemap_path)
        print('사이트맵 제출 성공:', SITEMAP)
    try:
        result = api(token, 'GET', sitemap_path)
    except RuntimeError:
        if status_only:
            raise
        print('제출은 성공했으나 처리 상태 조회에 실패했습니다. --status로 다시 확인하세요.')
        return
    print(json.dumps({key: result.get(key) for key in (
        'path', 'lastSubmitted', 'lastDownloaded', 'isPending', 'errors', 'warnings', 'contents')},
        ensure_ascii=False, indent=2))
    print('제출 성공과 Google의 수집·색인 완료는 서로 다른 상태입니다.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, help='Desktop OAuth client JSON (outside repository)')
    parser.add_argument('--token-file', type=Path, default=CONFIG / 'token.json')
    parser.add_argument('--status', action='store_true', help='Read status without submitting again')
    args = parser.parse_args()
    try:
        execute(access_token(args), args.status)
    except (RuntimeError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print('Google 인증에 실패했습니다. OAuth 설정과 브라우저 동의를 확인하세요.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
