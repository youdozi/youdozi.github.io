---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "Четыре бесплатных сервиса поддоменов для домашнего сервера Nginx",
  "description": "Для домашней сети с меняющимся IP, портфолио разработчика и самостоятельного управления зоной DNS подойдут разные сервисы.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e",
  "draftSha256": "146ba089042d40f4dc9f19231a5c09dd2f69e408ea56ba9832c39373ea99a110",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "ce67844b72beb7d028d68ceb5fab80ea752b9cf1879179e92a69310b0ac23029",
  "publishedAt": "2026-11-28T04:45:08.727Z",
  "updatedAt": "2026-11-28T04:45:08.727Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:08.727Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

Nginx уже работает дома. Какое имя дать посетителям? Все четыре сервиса предоставляют бесплатные поддомены в домене оператора. За сервер и доступ к нему извне отвечаете вы.

## Доступен ли сервер из другой сети?

DDNS обновляет IP-адрес, который возвращает DNS. Дойдёт ли соединение до Nginx, зависит от подключения, маршрутизатора и межсетевого экрана. Если провайдер использует CGNAT, проброса порта на домашнем маршрутизаторе может быть недостаточно. Если адрес WAN входит в диапазон `100.64.0.0/10`, уточните у провайдера, доступен ли публичный IPv4. [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## Выберите способ управления именем

| Сервис | Как управлять именем | Для чего подходит |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | Клиент обновляет адрес для `name.duckdns.org`. API умеет определять IPv4 автоматически. При обновлении IPv6 укажите адрес явно. | Первый опыт с меняющимся публичным IPv4. |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | Имя узла и API для обновления записей A, AAAA и префикса IPv6. | IPv6 или двойной стек. Корпоративного SLA нет. |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | Отправьте запрос на включение изменений в GitHub и дождитесь проверки. Команда просит писать заявку самостоятельно. | Портфолио разработчика. Если IP часто меняется, удобнее DDNS. |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | До подачи заявки подготовьте авторитетные серверы имён. После одобрения и делегирования по NS вы управляете A и AAAA в своей зоне. | Самостоятельное управление записями DNS. Динамическое обновление настраивается отдельно. |

## Проверьте выбранное имя

![Проверить адрес WAN → Выбрать способ обновления → Запросить записи DNS → Проверить доступ извне](/assets/diagrams/technical/ru-2026-11-28-nginx-free-subdomains.svg)

Для первого опыта убедитесь, что у вас есть публичный IPv4, и направьте на него одно имя Duck DNS. Установив dig, замените имя в примере и запросите оба типа записей. A должна содержать ваш публичный адрес. Если публикуете AAAA, проверьте доступ по IPv6 из другой сети.

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

Сравнение основано на документации сервисов. Мы не регистрировали учётные записи и не запрашивали имена.

[Локальная практика с приложением для заметок](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Как подключить Duck DNS к Nginx с помощью ИИ и проверить путь от DNS до HTTPS](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
