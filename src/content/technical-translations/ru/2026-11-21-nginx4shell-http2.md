---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-21-nginx4shell-http2",
  "routeSlug": "2026-11-21-nginx4shell-http2",
  "kind": "post",
  "title": "Руководство по Nginx4Shell — затронутые версии NGINX HTTP/2 и исправления",
  "description": "Условия проявления, исправленные версии и временная мера для уязвимостей HTTP/2 в NGINX CVE-2026-123007 и CVE-2026-123633. Пример на Python поможет определить приоритет обновления.",
  "categories": [
    "security"
  ],
  "tags": [
    "nginx",
    "http2",
    "patch-management",
    "cve-2026-123007",
    "cve-2026-123633"
  ],
  "sourcePath": "src/content/posts/en/2026-11-21-nginx4shell-http2.md",
  "sourceSha256": "51daac7a022b582074f762f0ce0c07d617f4af8535152688b060235117af16c2",
  "draftSha256": "6185691d50143d73f73b9e86c73cf8508b48e1f3dd79c3a32273f56a4d99ddb9",
  "manifestPath": ".pipeline/technical-translations/batch-175/manifest.json",
  "manifestSha256": "de1d6420b28e3a41bd670b52f3db93c0a08645e7821632b38b9c35d9f9d8517f",
  "publishedAt": "2026-11-21T00:38:31.366Z",
  "updatedAt": "2026-11-21T00:38:31.366Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 175,
    "approvedAt": "2026-11-21T00:38:31.366Z",
    "basis": "The site owner explicitly asked to publish the Nginx4Shell guide in the supported languages. This records authorization to publish these editions."
  }
}
---

**Сначала проверьте, какие слушатели NGINX принимают HTTP/2.** Опубликованные 18 ноября 2026 года уязвимости CVE-2026-123007 и CVE-2026-123633 могут привести к повреждению памяти при обработке HTTP/2. При определённых условиях рабочий процесс может аварийно завершиться либо возможно удалённое выполнение кода с правами этого процесса. В NGINX Open Source уязвимости исправлены в stable **1.30.7** и mainline **1.31.9**. Для пакетов дистрибутивов, NGINX Plus и продуктов Ingress проверяйте исправленные версии по уведомлениям поставщика. [Уведомления безопасности NGINX](https://nginx.org/en/security_advisories.html) · [Обновление безопасности F5 от 18 ноября](https://my.f5.com/s/article/K000164058)

## Какие конфигурации затронуты?

**Nginx4Shell** используется здесь как название для поиска. Указывайте оба номера CVE отдельно в заявках на изменение и реестрах активов, чтобы правильно сопоставить уведомления и статус исправления для каждого продукта.

| CVE | Условия и последствия | Затронутые версии NGINX Open Source |
| --- | --- | --- |
| CVE-2026-123007 | NGINX может повредить память при обработке клиентского трафика HTTP/2. Если HTTP/2 включён, проверьте и серверы, которые отдают только статические файлы. | 1.9.5–1.30.6 и 1.31.0–1.31.8 |
| CVE-2026-123633 | При передаче клиентского запроса HTTP/2 на вышестоящий сервер NGINX в определённых условиях может обратиться к уже освобождённой памяти. В первую очередь проверьте обратные прокси с HTTP/2. | 1.19.7–1.30.6 и 1.31.0–1.31.8 |

Обе уязвимости исправлены в стабильной версии 1.30.7. Хотя номер выше, чем у 1.30.7, **версия 1.31.8 остаётся затронутой**. Обновление также исправляет проблемы в HTTP/3, DNS-резолвере и почтовом прокси. Если временно изменили настройки HTTP/2, продолжайте готовить установку исправления для продукта. [Анонсы версий NGINX](https://nginx.org/news.html) · [F5 CVE-2026-123007](https://my.f5.com/s/article/K000163926) · [F5 CVE-2026-123633](https://my.f5.com/s/article/K000163928) · [Рекомендации CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

## Проверьте запущенный продукт и путь HTTP/2

1. **Определите происхождение запущенного бинарного файла.** На виртуальной машине проверьте исполняемый файл и пакет, которые использует служба. В контейнере проверьте фактически запущенный образ и его дайджест. Выполните `nginx -V` в нужной среде, чтобы увидеть версию и параметры сборки. Некоторые дистрибутивы, в том числе Ubuntu 24.04 LTS, переносят исправления в уже выпущенные версии. В уведомлении Ubuntu исправленный пакет для этого выпуска указан как `1.24.0-2ubuntu7.20`. [Параметры командной строки NGINX](https://nginx.org/en/docs/switches.html) · [Ubuntu USN-9159-1](https://ubuntu.com/security/notices/USN-9159-1)
2. **Проверьте участок от клиента или внешнего прокси до NGINX.** Браузер может связываться с CDN по HTTP/2, а CDN может использовать другой протокол для обращения к исходному серверу NGINX. Просмотрите фактическую конфигурацию работающей службы с помощью `nginx -T`. Проверьте блоки `http` и `server`, подключаемые файлы и используемый синтаксис. Полная конфигурация может содержать внутренние адреса и секреты. Просматривайте её в среде, где это разрешено. [Документация модуля HTTP/2 в NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
3. **Сначала обновите затронутые экземпляры, которые принимают внешние запросы.** После развёртывания убедитесь, что процессы используют новый бинарный файл или образ. Выполните проверку конфигурации `nginx -t`, затем проверьте обычные HTTP-запросы, состояние вышестоящих серверов, долю ошибок и перезапуски рабочих процессов. В кластере убедитесь, что реплики со старым образом не остались. [Рекомендации CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

Если немедленное обновление невозможно, отключение HTTP/2 на затронутых слушателях может снизить риск для обеих CVE. В актуальном синтаксисе используйте `http2 off;`. В старом синтаксисе удалите опцию `http2` из директивы `listen`. До изменения проверьте маршруты, зависящие от HTTP/2, например gRPC. После изменения проверьте фактические подключения к этим слушателям и штатные запросы к службе. [Документация по настройке HTTP/2 в NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html) · [Рекомендации Red Hat по снижению риска](https://access.redhat.com/security/vulnerabilities/RHSB-2026-019)

## Практика — определяем порядок обновления по результатам проверки

Пример принимает **происхождение продукта, версию и состояние HTTP/2**, которые проверил оператор. Он работает на Python 3.10 и новее и использует только стандартную библиотеку. Сведения из предыдущих шагов помогут определить приоритет установки исправлений.

![Введите происхождение продукта и его версию. Для пакетов дистрибутива и продуктов стороннего поставщика сверьтесь с его уведомлением. Если оригинальная версия NGINX входит в затронутый диапазон, используйте состояние HTTP/2, чтобы выбрать между приоритетной установкой исправления и дополнительной проверкой конфигурации.](/assets/diagrams/technical/ru-2026-11-21-nginx4shell-http2.svg)

Сохраните скрипт как `nginx_http2_triage.py`. Значение `upstream` используйте только для исходных выпусков Open Source от проекта NGINX. Для пакетов с перенесёнными исправлениями или образов поставщика укажите `vendor`. Если происхождение продукта или конфигурация слушателя ещё не проверены, укажите `unknown` для соответствующего параметра.

```python
import argparse
import re


def upstream_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", value):
        raise argparse.ArgumentTypeError("use an upstream version such as 1.30.7")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def triage(origin: str, value: str, http2: str) -> str:
    if origin != "upstream":
        return "CHECK_VENDOR_ADVISORY"

    version = upstream_version(value)
    if version[0] != 1 or version > (1, 31, 9):
        return "CHECK_CURRENT_ADVISORY"
    if (1, 30, 7) <= version < (1, 31, 0) or version == (1, 31, 9):
        return "UPSTREAM_FIX_VERSION"

    affected = [
        cve
        for cve, first_version in (
            ("CVE-2026-123007", (1, 9, 5)),
            ("CVE-2026-123633", (1, 19, 7)),
        )
        if version >= first_version
    ]
    if not affected:
        return "OUTSIDE_LISTED_RANGES"

    action = {
        "on": "PRIORITIZE_PATCH",
        "off": "PATCH_STILL_REQUIRED",
        "unknown": "VERIFY_HTTP2_AND_PATCH",
    }[http2]
    return f"{action} {' '.join(affected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("origin", choices=("upstream", "vendor", "unknown"))
    parser.add_argument("version")
    parser.add_argument("http2", choices=("on", "off", "unknown"))
    args = parser.parse_args()
    try:
        print(triage(args.origin, args.version, args.http2))
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
```

```bash
python3 nginx_http2_triage.py upstream 1.31.8 on
python3 nginx_http2_triage.py upstream 1.30.7 on
python3 nginx_http2_triage.py upstream 1.19.6 unknown
python3 nginx_http2_triage.py vendor 1.24.0-2ubuntu7.20 on
```

При запуске этих команд на Python 3.13.0 получен следующий вывод.

```text
PRIORITIZE_PATCH CVE-2026-123007 CVE-2026-123633
UPSTREAM_FIX_VERSION
VERIFY_HTTP2_AND_PATCH CVE-2026-123007
CHECK_VENDOR_ADVISORY
```

Список CVE показывает **потенциально применимые к версии уязвимости**. Чтобы определить, действует ли условие с вышестоящим сервером для CVE-2026-123633, проверьте конфигурацию реального слушателя. Пример классифицирует введённые параметры по опубликованным диапазонам версий. Конфигурацию рабочего сервера и наличие исправлений проверяют отдельно.
