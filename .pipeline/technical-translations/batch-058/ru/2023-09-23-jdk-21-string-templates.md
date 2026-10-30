---
language: "ru"
translationKey: "2023-09-23-jdk-21-string-templates"
title: "Шаблоны строк Java: preview JDK 21, удаление в JDK 23 и альтернативы"
description: "Запустите полный пример String Templates на JDK 21, разберитесь с удалением в JDK 23 и замените STR проверенными стандартными средствами форматирования Java."
state: "draft"
sourcePath: "src/content/posts/en/2023-09-23-jdk-21-string-templates.md"
sourceSha256: "82b3cfe0b6ea0478f27df7cea88e1b5974a7e661e6be9f9baa20c5d663c7a01b"
---
Шаблоны строк были предварительными возможностями в JDK 21 и 22 и были удалены в JDK 23. Добавление `--enable-preview` в JDK 23 не возвращает `STR`. Для кода, который должен выйти за пределы этих preview, используйте стандартные строковые API или сериализатор нужного формата. Изменение описано в [объяснении удаления от Oracle](https://inside.java/2024/06/20/newscast-71/).

## Порядок обработки

![Показан стандартный FormattingExample, а не исторический пример preview. Он сравнивает три формы форматирования и проверяет экранирование апострофа в MessageFormat.](2023-09-23-jdk-21-string-templates.svg)

Показан стандартный FormattingExample, а не исторический пример preview. Он сравнивает три формы форматирования и проверяет экранирование апострофа в MessageFormat.

## Какой JDK может запустить старый пример?

| JDK | Статус String Templates | Что делать |
| --- | --- | --- |
| 21 | Preview | Компилировать и запускать на JDK 21 с включённым preview. |
| 22 | Вторая preview | Использовать согласованные компилятор JDK 22, среду и настройки preview. |
| 23 | Удалены | Заменить синтаксис preview; флаги не возвращают удалённую возможность. |

Флаг компилятора `--release` не позволяет оживить старую preview на новом компиляторе. [Руководство Oracle по preview](https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html) требует компилятор соответствующего выпуска.

## Запуск исторического примера JDK 21

Сохраните полный класс как `Example.java`. Здесь нужен JDK 21, даже если по умолчанию выбран другой JDK.

```java
public class Example {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        String result = STR."\{x} plus \{y} equals \{x + y}";
        System.out.println(result);
    }
}
```

Проверьте выбранные инструменты, затем скомпилируйте и запустите в каталоге с файлом:

```sh
javac -version
java -version
javac --enable-preview --release 21 Example.java
java --enable-preview Example
```

Вывод: `2 plus 3 equals 5`. Компилятор также сообщает об использовании preview. В этой preview JDK 21 `STR` импортируется неявно; отсутствие процессора в последующем JDK не исправить добавлением import. См. [руководство по String Templates в JDK 21](https://docs.oracle.com/en/java/javase/21/language/string-templates.html).

## Замена синтаксиса preview стандартными API

Сохраните следующий код как `FormattingExample.java`. Он использует стандартные API без флагов preview. Полный класс работает на Java 17. Здесь `String.format` и `MessageFormat` используют явно заданную локаль для воспроизводимого числового вывода.

```java
import java.text.MessageFormat;
import java.util.Locale;

public class FormattingExample {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        System.out.println(x + " plus " + y + " equals " + (x + y));
        System.out.println(String.format(Locale.ROOT, "%1$d plus %2$d equals %3$d", x, y, x + y));
        MessageFormat format = new MessageFormat("{0} plus {1} equals {2}", Locale.ROOT);
        System.out.println(format.format(new Object[] {x, y, x + y}));
        System.out.println(new MessageFormat("It''s {0}", Locale.ROOT)
            .format(new Object[] {"ready"}));
    }
}
```

```sh
javac FormattingExample.java
java FormattingExample
```

Вывод:

```text
2 plus 3 equals 5
2 plus 3 equals 5
2 plus 3 equals 5
It's ready
```

| Задача | Подходящий API | Что сохранить |
| --- | --- | --- |
| Короткое выражение | `+` | Скобки вокруг `x + y` явно задают арифметическую операцию. |
| Повторные добавления | `StringBuilder` | Полезен при постепенном построении текста. |
| Строка формата | `String.format` или `.formatted` | `%d` и `%s` следуют правилам Formatter; для явной локали используйте `String.format(Locale.ROOT, ...)`. |
| Локализованный шаблон сообщения | `MessageFormat` | Использует нумерованные аргументы, массив объектов и другие правила кавычек. |

`MessageFormat` рассматривает одинарные кавычки как синтаксис шаблона. Удвоение в `It''s {0}` даёт буквальный апостроф, показанный выше. Замена шаблона `%s` на `{0}` также требует сменить API и проверить его поведение с локалью. [API MessageFormat](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html), [API String](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html).

## Отделяйте форматирование от кодирования

Ни `STR`, ни обычное форматирование не делают произвольные значения безопасными JSON, SQL или HTML. Используйте сериализатор JSON, связывание параметров SQL или HTML-экранирование системы рендеринга для нужного формата. Строка, корректная на простых примерах, может сломаться при кавычках или обратных косых чертах в значении.

Оба полных класса компилировались и запускались приведёнными командами: preview на JDK 21.0.1, стандартная альтернатива на JDK 17.0.8.1 и 21.0.1. Строки JDK 22 и 23 описывают документированную историю; в этой среде они не выполнялись.

Обновление JDK также влияет на совместимость фреймворков. Для старого Spring-приложения см. [порядок миграции с Spring Boot 2.7 на 3.0](/en/posts/2023-09-08-springboot3-migration/).
