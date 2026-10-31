---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2021-07-23-number-word",
  "routeSlug": "2021-07-23-number-word",
  "kind": "post",
  "title": "用 Java String.replace 转换英文数字单词",
  "description": "通过字面量替换规范化数字与 zero 到 nine 单词的有效混合输入，区分 replace 与 replaceAll，并说明整数范围和适用条件。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-number-word.md",
  "sourceSha256": "28614468f78703f7e406439ee8b23b83e06091ae7f42ed9835cd50c6d1bb2e87",
  "draftSha256": "4404519619b5aabd16ff36af55610e2dc0c748749ca3e674573ee8a310a12a27",
  "manifestPath": ".pipeline/technical-translations/batch-055/manifest.json",
  "manifestSha256": "1fe8bbde2d19f5780ba08f158519bd2d55fdec1dc863ec3bd9126705ddda372f",
  "publishedAt": "2026-10-31T15:21:36.540Z",
  "updatedAt": "2026-10-31T15:21:36.540Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.540Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
对于数字字符与数字单词混合的有效输入，先把 `zero` 到 `nine` 这些固定单词替换为数字，再解析为整数。搜索项都是字面量，因此用 `String.replace` 即可，不需要 `replaceAll`。

[题目](https://school.programmers.co.kr/learn/courses/30/lessons/81301)保证输入只包含有效的小写数字单词和数字，结果介于 1 和 2,000,000,000 之间，且没有前导零。这不是解析一般英文数值表达式的解析器。

## 处理流程

![将 zero 到 nine 这些固定单词按字面量替换为数字字符，再解析得到的十进制字符串。](/assets/diagrams/technical/zh-CN-2021-07-23-number-word.svg)

将 zero 到 nine 这些固定单词按字面量替换为数字字符，再解析得到的十进制字符串。

## 替换十个固定单词

将完整类保存为 `Solution.java`。不需要额外导入；原文中的代码已按 Java 11 目标编译并执行。

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html)执行字面量替换。`replaceAll` 将第一个参数解释为正则表达式。这里的十个单词都不需要正则语法。

例如，`one4seveneight` 变成 `1478`，`23four5six7` 变成 `234567`。原本就只有数字的输入，如 `123`，仍得到 123。`two` 后接九个 `zero` 单词会得到 2,000,000,000，处于 int 范围内。

替换产生的数字字符不会引入另一个数字单词，而且这十个单词中没有任何一个包含集合中的另一个单词，因此该顺序可行。无效单词、空格、大写输入以及超出范围的数值均不在题目保证内。对任意输入解析失败时，此方法不会将其修复为有效整数。

固定单词只有十个，因此时间复杂度相对于输入长度为 O(n)。字符串不可变，替换过程中可能分配中间字符串；额外空间为 O(n)。没有基准测试证明此方法在这些小输入上比其他解析器更快。

对于适合使用正则表达式的转换，可对照[新 ID 规范化](/en/posts/2021-07-19-new-id/)。
