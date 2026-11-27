---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-27-droiddesk-android-linux-desktop",
  "routeSlug": "2026-11-27-droiddesk-android-linux-desktop",
  "kind": "post",
  "title": "Как устроен DroidDesk · Откуда на телефоне с Android берётся рабочий стол Linux?",
  "description": "У отдельного APK и установочного скрипта для Termux разные среды выполнения и способы вывода изображения. Разберём, что стоит проверить на своём телефоне.",
  "categories": [
    "tips"
  ],
  "tags": [
    "android",
    "linux",
    "termux"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-droiddesk-android-linux-desktop.md",
  "sourceSha256": "656b9e1b21a758a366d894876650b607e9bd2eadcb535e4a0565a68566807a1f",
  "draftSha256": "4a05586c9d28a99b211eb0e5ab46d3fb89c66e388740ae79019d304b71ac71ce",
  "manifestPath": ".pipeline/technical-translations/batch-130/manifest.json",
  "manifestSha256": "155408f4218bb7fd2e43ec0f8dcb31522024a85ed96fb84e2f9768840357e28c",
  "publishedAt": "2026-11-27T06:13:21.434Z",
  "updatedAt": "2026-11-27T06:13:21.434Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 207,
    "approvedAt": "2026-11-27T06:13:21.434Z",
    "basis": "Explicit user request to publish the approved DroidDesk manuscript from item 129 in all nine languages (item 130)."
  }
}
---

Можно ли подключить клавиатуру к старому телефону с Android и работать в редакторе и браузере для Linux? DroidDesk — проект с открытым исходным кодом, который запускает рабочий стол Linux поверх Android. Перед установкой полезно разобраться, как именно это делают отдельный APK и установочный скрипт для Termux.

В основе статьи — описание выпуска и исходный код orailnoor/DroidDesk v1.3.1 по состоянию на 27 ноября 2026 года. Я не устанавливал APK на физическое устройство и не измерял производительность отдельных приложений. [Описание выпуска](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

## Чем APK отличается от скрипта для Termux?

| Способ установки | Среда выполнения | Вывод изображения |
| --- | --- | --- |
| Отдельный APK без root-прав | Рабочий стол по умолчанию во встроенном Termux, дополнительно можно установить Debian для запуска через PRoot | Встроенный Termux:X11 |
| Отдельный APK с root-правами | Файловая система Ubuntu для ARM64 в окружении chroot | Встроенный Termux:X11 |
| Установочный скрипт для Termux | Отдельно установленный Termux, PRoot для пакетов дистрибутива | Отдельное приложение Termux:X11 или, по желанию, VNC |

![Отдельный APK использует встроенный Termux:X11. Скрипт для Termux выводит изображение через отдельное приложение Termux:X11 или VNC.](/assets/diagrams/technical/ru-2026-11-27-droiddesk-android-linux-desktop.svg)

Согласно README, на устройствах без root-прав APK обходится без PRoot. Для рабочего стола по умолчанию это верно: он запускается непосредственно в Termux. Однако в v1.3.1 модуль LinuxRuntime позволяет дополнительно установить Debian и содержит средство запуска через PRoot. Даже в одном приложении условия работы программы могут различаться в зависимости от того, запускаете вы её с основного рабочего стола или из Debian. [README](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md) · [LinuxRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/LinuxRuntime.kt) · [ChrootRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/ChrootRuntime.kt)

## На что способен ваш телефон?

Начните с одной нужной вам программы. Проект приводит в пример Firefox, LibreOffice и VS Code. В описании v1.3.1 также упомянуты исправления ошибок установки и запуска, которые затрагивали, в частности, пакет, необходимый Firefox, и VS Code. После появления значка редактора стоит проверить привычные расширения, метод ввода и пути к файлам. [Описание выпуска](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

Возможности графики тоже зависят от устройства. В коде предусмотрены вариант с Turnip и Zink для Adreno и программный рендеринг через llvmpipe. Если вы хотите работать в таком требовательном приложении, как Blender, проверьте, задействовано ли ускорение на вашем телефоне и насколько плавно идёт работа с реальным проектом. При сборке программ под PRoot частые обращения к файлам могут создавать дополнительные накладные расходы. [Ограничения PRoot](https://github.com/termux/proot-distro#limitations)

Прежде чем подключать внешний монитор, проверьте, поддерживает ли телефон видеовыход через USB-C. В описанной проектом схеме с Raspberry Pi плата принимает сеанс VNC, который предоставляет скрипт Termux, и выводит изображение на монитор. У отдельного APK другой способ вывода — встроенный X11. [Подключение монитора](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md#for-monitor-output--optional-)

## Что попробовать в первую очередь?

Если у вас устройство с Android на ARM64, найдите APK на официальной странице выпусков проекта и начните с экрана телефона. Например, наберите в редакторе текст на корейском, сохраните файл, заново откройте сеанс и загрузите тот же файл. Если всё получилось, подключите клавиатуру и мышь или внешний монитор и попробуйте продолжить привычную работу. DroidDesk интересен возможностью выяснить, какие инструменты Linux пригодятся на телефоне, который у вас уже есть. Для работы с документами сначала проверьте ввод и сохранение, для разработки — нужные пакеты и расширения, для графики — ускорение и отзывчивость экрана. [Конфигурация сборки Android](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/build.gradle.kts)

[Как проверить, сколько места занимает Docker Desktop на Mac](../2026-11-27-docker-desktop-mac-disk-space/)
