---
"language": "ko"
"translationKey": "2026-11-01-ai-agent-permission-boundaries"
"routeSlug": "2026-11-01-ai-agent-permission-boundaries"
"title": "AI 에이전트 권한 설계: 예상하지 못한 사고의 범위를 줄이는 방법"
"description": "AI 에이전트의 permission을 파일·명령·네트워크·실행 계정으로 나누고, 승인 범위와 관리자 우회 권한을
  분리하는 방법입니다. 실행 가능한 권한 판정 예제로 기본 거부·승인 만료·재사용 차단을 확인합니다."
"categories":
  - "security"
"tags":
  - "ai-agent"
  - "permissions"
  - "least-privilege"
  - "sandbox"
  - "approval"
  - "security"
"kind": "post"
"publishedAt": "2026-11-01T13:12:07.154Z"
"updatedAt": "2026-11-01T13:12:07.154Z"
"reviewedAt": "2026-11-01"
"reviewStatus": "source-audited"
"reviewScope": "공식 OWASP·GitHub·Kubernetes 문서 대조와 자체 한영 의미 검토. Python 권한 예제
  10건·회귀 변이 3건 검증. 운영 권한 게이트웨이·샌드박스 구축 시험은 수행하지 않음."
"reviewSources":
  - "https://genai.owasp.org/llmrisk/llm062025-excessive-agency/"
  - "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"
  - "https://docs.github.com/en/repositories/configuring-branches-and-merges-in\
    -your-repository/managing-protected-branches/about-protected-branches"
  - "https://docs.github.com/en/actions/reference/workflows-and-actions/workflo\
    w-syntax#permissions"
  - "https://kubernetes.io/docs/concepts/security/rbac-good-practices/"
---

**AI 에이전트의 예상하지 못한 행동으로 인한 사고를 줄이려면, 실행 가능한 작업과 접근 대상을 제한하고 영향이 큰 작업에 구체적인 승인 경계를 둬야 합니다.** 파일을 잘못 고치거나 요청을 넓게 해석하더라도 운영 데이터 삭제·외부 전송·보호 규칙 우회로 곧바로 이어지지 않게 만드는 것입니다. 권한 설계는 모든 실수를 없애지는 못하지만, 실수가 영향을 미치는 범위를 줄일 수 있습니다.

여기서 permission은 에이전트에게 보여 주는 도구 목록뿐 아니라 실제 실행 환경과 외부 서비스 계정이 가진 권한까지 포함합니다. [OWASP의 Excessive Agency 설명](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)도 과도한 도구 기능·권한·자율성을 주요 위험으로 다루며, 최소 권한과 영향이 큰 작업의 승인을 권고합니다.

## “작업을 완료하라”가 권한 확대로 이어질 때

다음은 설계상 위험을 설명하기 위한 가상 시나리오입니다. 사용자가 글 게시를 요청했고 CI도 통과했지만, 저장소는 별도의 PR 승인을 요구합니다. 에이전트가 이 상태를 단순한 작업 장애로 해석해 관리자 권한으로 병합하면, 게시 작업과 보호 규칙 예외 처리가 하나의 권한처럼 섞입니다.

이 경우 확인할 것은 두 가지입니다. **현재 산출물을 게시할 권한이 있는가, 그리고 보호 규칙의 예외를 허용할 권한도 있는가?** 일반적인 게시 요청을 관리자 우회까지 허용한 것으로 자동 확장하면 예상하지 못한 변경이 생길 수 있습니다. GitHub의 브랜치 보호는 설정에 따라 관리자나 우회 권한 보유자에게 적용되지 않을 수 있으므로, 보호 규칙과 실행 계정의 우회 가능성을 함께 확인해야 합니다. [GitHub 보호 브랜치와 우회 설정](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

권한 거부가 발생하면 같은 효과를 다른 명령·API·계정으로 다시 시도해도 되는지 먼저 정책으로 판정합니다. 승인이나 권한 부족으로 막힌 작업은 정책이 허용한 대기·예외 절차로 넘깁니다. 서비스 일시 장애에 대한 재시도와 권한 거부에 대한 대응을 구분해야 합니다.

## 안내문과 실제 권한 통제는 서로 다른 역할을 한다

`AGENTS.md`나 프롬프트의 “운영 DB를 수정하지 말라”는 지시는 작업 의도를 전달합니다. 실제 DB 연결 계정에도 읽기 권한만 부여하면 잘못 생성된 쓰기 요청을 DB가 거부할 수 있습니다. 안내문은 모델의 행동을 돕고, 실행 환경과 서비스의 인가는 행동이 일으킬 수 있는 효과를 제한합니다.

| 계층 | 제한할 대상 | 설계 예시 |
| --- | --- | --- |
| 작업 지침 | 수행 범위와 중단 조건 | 초안 작성은 허용하고 게시·관리자 우회는 별도 작업으로 정의 |
| 실행 환경 | 파일·프로세스·네트워크 접근 | 작업 폴더만 쓰기 허용, 운영 비밀 미주입, 필요한 외부 목적지만 연결 |
| 도구 게이트웨이 | 작업과 인자의 조합 | `publish`의 사이트·산출물 해시를 확인하고 임의 명령 실행은 제공하지 않음 |
| 외부 서비스 | 실제 자격증명의 권한 | 저장소·DB·클러스터별 제한된 서비스 계정과 보호 규칙 적용 |

게이트웨이를 두더라도 에이전트 프로세스에 관리자 토큰이 그대로 있다면 직접 API를 호출하는 경로가 남습니다. 실행 권한을 가진 자격증명은 제한된 실행 서비스가 보관하고, 에이전트는 그 서비스에 구조화된 요청을 보내도록 분리하는 방식을 검토할 수 있습니다. 정책 파일과 승인 저장소도 에이전트가 수정할 수 없어야 합니다.

## 명령 이름보다 작업의 효과를 제한하기

“테스트 명령은 허용”이라는 규칙만으로 실행 환경이 안전해지지는 않습니다. 테스트·빌드·의존성 설치는 저장소나 패키지의 코드를 실행할 수 있습니다. 신뢰하지 않는 코드를 실행하는 작업 공간에는 운영 자격증명을 넣지 않고, 필요한 파일·네트워크·자원만 제공해야 합니다. 컨테이너를 사용해도 호스트의 민감한 경로나 Docker 소켓을 연결하면 격리 범위를 다시 점검해야 합니다.

읽기 작업에도 대상과 데이터 범위가 필요합니다. 비밀 파일을 읽어 외부로 전송하거나, 조회 API의 쿼리 문자열에 민감정보를 담는 행동은 데이터를 바꾸지 않더라도 사고를 일으킵니다. 외부 문서·웹페이지·도구 응답에 포함된 명령문도 작업 승인으로 취급하지 않습니다. [OWASP의 프롬프트 인젝션 설명](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)은 외부 콘텐츠를 통한 간접 인젝션을 다룹니다.

GitHub Actions의 토큰은 다음처럼 필요한 범위만 선언할 수 있습니다. 아래는 workflow에 넣는 설정 조각입니다.

```yaml
permissions:
  contents: read
```

이 설정은 해당 `GITHUB_TOKEN`의 권한을 제어합니다. 명시하지 않은 권한은 `none`이 되지만, 작업에 별도로 전달한 PAT·클라우드 키·DB 자격증명의 권한까지 제한하지는 않습니다. 에이전트 실행기에 어떤 자격증명이 실제로 들어가는지 함께 확인해야 합니다. [GitHub Actions permissions 문법](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

Kubernetes에서도 일반 작업 계정의 `escalate`·`bind`·`impersonate` 권한은 별도로 검토합니다. 이런 권한은 다른 권한을 획득하거나 다른 주체로 행동하는 경로가 될 수 있습니다. [Kubernetes RBAC 권고](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)

## 승인은 실행할 산출물과 대상에 연결하기

승인을 받을 때는 “계속 진행할까요?”만 보여 주기보다 작업·대상·변경 내용을 확인할 수 있게 합니다. 예를 들어 게시 승인은 사이트 ID, 검토한 산출물 해시, 실행 주체, 유효 기간과 한 번만 사용할 승인 ID에 연결할 수 있습니다. 승인 뒤 본문이나 배포 이미지가 바뀌면 새 산출물이 기존 승인 범위에 들어가는지 다시 판정합니다.

모든 읽기·초안 편집마다 승인을 요구할 필요는 없습니다. 사전에 승인한 작업 범위 안에서는 계속 실행하고, 범위를 벗어나거나 정책상 별도 승인이 필요한 효과에 도달했을 때 멈추도록 구성합니다. 승인 피로를 줄이면서도 게시·삭제·외부 전송·관리자 예외의 경계를 유지하는 방식입니다. 관리자 예외가 꼭 필요한 운영 절차는 일반 실행기와 분리된 주체·권한·감사 경로로 다룹니다.

## 실행 예제: 승인해도 정책 밖의 작업은 거부한다

다음 코드는 권한 판정 순서를 보여주는 **외부 효과가 없는 단일 프로세스 예제**입니다. `repo:demo` 같은 값은 정해진 논리 자원 ID이며 실제 파일 경로·URL이 아닙니다. `read`와 초안 `edit`는 정책으로 허용하고, `publish`는 같은 주체·요청에 대한 유효한 승인이 있어야 허용합니다. 정책에 없는 관리자 우회는 승인 객체가 있어도 거부합니다.

![정책의 허용 범위를 확인하고 승인 필요한 게시 요청에 대해 승인 존재·주체와 산출물 일치·만료·재사용 여부를 검사한 뒤 허용하는 흐름](/assets/diagrams/2026-11-01-ai-agent-permission-boundaries-ko.svg)

그림은 승인 필요한 `publish` 경로를 보여줍니다. 코드에서 `read`·초안 `edit`가 즉시 허용되는 분기는 생략했습니다. 어느 검사에서든 멈추면 다음 단계나 실제 게시를 실행하지 않습니다.

Python 3.10 이상에서 아래 코드를 `permission_gate.py`로 저장해 `python3 permission_gate.py`를 실행합니다. 외부 통신·자격증명·추가 패키지는 필요하지 않습니다.

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Request:
    action: str
    target: str
    artifact: str


@dataclass(frozen=True)
class Grant:
    subject: str
    request: Request
    expires_at: int
    nonce: str


class Gate:
    def __init__(self):
        self.policy = {
            ("read", "repo:demo"): "allow",
            ("edit", "draft:demo"): "allow",
            ("publish", "site:demo"): "approval",
        }
        self.used = set()

    def check(self, subject, request, grant, now):
        mode = self.policy.get((request.action, request.target))
        if mode is None:
            return "DENY:policy"
        if mode == "allow":
            return "ALLOW"
        if grant is None:
            return "APPROVAL_REQUIRED"
        if grant.subject != subject or grant.request != request:
            return "DENY:scope"
        if now >= grant.expires_at:
            return "DENY:expired"
        if grant.nonce in self.used:
            return "DENY:replay"
        self.used.add(grant.nonce)
        return "ALLOW"


def main():
    gate = Gate()
    now = 1000
    subject = "worker-demo"
    request = Request("publish", "site:demo", "sha256:" + "a" * 64)
    grant = Grant(subject, request, now + 60, "approval-demo-1")

    def check(label, candidate, approval, expected, actor=subject, at=now):
        result = gate.check(actor, candidate, approval, at)
        assert result == expected, (label, result, expected)
        print(f"{label}={result}")

    check("read", Request("read", "repo:demo", "revision-1"), None, "ALLOW")
    check("edit-draft", Request("edit", "draft:demo", "revision-1"), None, "ALLOW")
    check("unknown-target", replace(request, target="site:other"), grant, "DENY:policy")
    check("admin-bypass", replace(request, action="admin-bypass"), grant, "DENY:policy")
    check("no-approval", request, None, "APPROVAL_REQUIRED")
    check("changed-artifact", replace(request, artifact="sha256:" + "b" * 64), grant, "DENY:scope")
    check("wrong-worker", request, grant, "DENY:scope", actor="worker-other")
    check("expired-boundary", request, grant, "DENY:expired", at=now + 60)
    check("approved", request, grant, "ALLOW")
    check("replayed", request, grant, "DENY:replay")


if __name__ == "__main__":
    main()
```

Python 3.13.0에서 실행한 결과입니다. 아래 10개 합성 시나리오의 반환값을 확인했습니다.

```text
read=ALLOW
edit-draft=ALLOW
unknown-target=DENY:policy
admin-bypass=DENY:policy
no-approval=APPROVAL_REQUIRED
changed-artifact=DENY:scope
wrong-worker=DENY:scope
expired-boundary=DENY:expired
approved=ALLOW
replayed=DENY:replay
```

`Grant`는 승인 서비스가 발급·인증한 정보를 받았다고 가정합니다. 이 예제 자체는 승인자·실행 주체의 신원·권한·서명이나 입력 스키마를 검증하지 않으며, 데이터 클래스의 타입 주석도 런타임 검증을 대신하지 않습니다. 모델이 만든 JSON을 그대로 `Grant`로 바꿔 승인으로 인정하면 안 됩니다. `now=1000`, 60초, 해시와 승인 ID도 동작을 설명하는 합성 값이며 운영 권장값이 아닙니다.

실제 실행기는 승인 저장소에서 승인 정보를 읽고 게시할 산출물의 해시를 직접 계산해야 합니다. 에이전트가 보낸 해시만 비교하면 실제 본문과 다른 값을 제시할 수 있습니다. 정책·시각·실행 주체·대상도 신뢰된 실행 맥락에서 확인하며, 에이전트가 이 판정 함수를 건너뛰어 외부 API를 호출할 수 없도록 실행 경로와 자격증명을 제한합니다.

`used`는 프로세스 메모리에만 있으므로 재시작·다중 실행기 환경의 재사용을 막지 못합니다. 실제 실행 서비스에서는 승인 저장소의 원자적 소비, 승인 취소, 실행 직전의 정책·대상 재확인과 작업 멱등성이 필요합니다. 승인 소비 뒤 실행이 실패했을 때의 재시도도 같은 작업 ID와 실제 실행 결과를 기준으로 처리해야 합니다. 이 코드는 `ALLOW`를 반환할 뿐 게시 API를 호출하지 않습니다.

## 도입할 때 먼저 확인할 것

현재 에이전트가 접근할 수 있는 파일·토큰·계정과 실제로 호출할 수 있는 API를 목록화합니다. 명시적으로 연결한 도구 외에도 셸 환경 변수, 홈 디렉터리의 인증 파일, 네트워크 경로를 확인해야 합니다. 처음에는 읽기·격리 초안 작업부터 허용하고, 영향이 큰 실행은 범위가 좁은 전용 도구로 추가합니다.

그다음 승인 없는 게시, 승인 후 산출물 변경, 만료·재사용, 다른 작업 주체, 미등록 자원, 관리자 우회 요청이 거부되는지 시험합니다. 외부 문서가 권한 확대를 요구해도 같은 통제가 유지되는지 확인합니다. 에이전트가 정책을 수정하거나 실행 서비스의 토큰을 직접 읽을 수 있다면 그 경로부터 닫아야 합니다.

감사 로그에는 요청 ID, 주체, 대상, 산출물 해시, 적용 정책, 승인 ID와 실행 결과를 연결하되 토큰·민감한 본문을 그대로 남기지 않습니다. 이상 행동을 발견하면 새 작업 접수 중지와 자격증명 회수를 통해 추가 영향을 제한합니다. 이미 전송한 데이터나 완료된 외부 변경은 권한 회수만으로 되돌아오지 않으므로, 복구 절차를 실행 통제와 함께 준비합니다.

코드·테스트·배포·관측·DB 증거를 연결하는 운영 흐름은 [AI 에이전트 운영 기법](/ko/posts/2026-10-31-ai-agent-operations/)에서 이어서 볼 수 있습니다.
