---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-25-microsoft-365-code-red",
  "routeSlug": "2026-11-25-microsoft-365-code-red",
  "kind": "post",
  "title": "从 Microsoft 365“Code Red”学习故障应对：转移流量前要检查什么",
  "description": "从 Microsoft 365 故障看故障转移的接收上限、恢复期间的重连负载和共享故障记录。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "microsoft-365",
    "incident-response",
    "failover",
    "load-shedding"
  ],
  "sourcePath": "src/content/posts/en/2026-11-25-microsoft-365-code-red.md",
  "sourceSha256": "2df9b4039ebb04013f04e21b144e3cb3780236a74b97dd9dcd885df36569a389",
  "draftSha256": "374d23c5e89f947185bbff2fc171a780ffb649ed206113e74b4e61d2a792bd86",
  "manifestPath": ".pipeline/technical-translations/batch-191/manifest.json",
  "manifestSha256": "3c11feea419e90c2b266ce8c92f61b8a1c397634ec1891b701c3c13c0a447504",
  "publishedAt": "2026-11-25T04:56:03.451Z",
  "updatedAt": "2026-11-25T04:56:03.451Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 194,
    "approvedAt": "2026-11-25T04:56:03.451Z",
    "basis": "User approved publication of this supplied manuscript in eight languages and authorized the localized diagrams on 2026-11-25; translation review is self-review, not human or native-speaker review."
  }
}
---

服务器无响应时，请求会转向正常服务器。通常，这让用户察觉不到几台服务器的停机。2026 年十一月的 Microsoft 365 故障中，同一机制却将故障带到了其他地区：接收请求的服务器也有相同缺陷，负载增加后缺陷在那里同样显现。[Microsoft 事后报告副本](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

![网关容量下降、Teams 流量转入和峰值需求叠加，转流随后将负载送到存在相同缺陷的服务器。](/assets/diagrams/technical/zh-CN-2026-11-25-microsoft-365-code-red.svg)

网关容量下降、Teams 流量转入和峰值需求叠加，转流随后将负载送到存在相同缺陷的服务器。

## 七月引入的缺陷为何在十一月显现？

根据 Microsoft 的事后报告，缺陷存在于 Microsoft 365 网络网关的 Windows 更新中。从七月起，更新历经数周部署，三个多月内未观察到客户受到影响。但核心数更多的新服务器可同时处理更多连接请求，可能加剧内部锁竞争。当时负载测试所用服务器的核心数较少，测试流量也与故障时不同。[Microsoft 事后报告副本](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

11 月 12 日，例行工作使部分网关容量不可用，Teams 流量转到了与 Exchange Online 共用的网关。服务一度运行正常。随着北美使用量接近平时峰值，服务器开始无响应，自动转流又增加了每台剩余服务器的负载。跨区域转流也把请求送到了存在相同缺陷的服务器。报告记录的**客户受到直接影响的时段约为 23 小时 50 分钟**；之后，延迟邮件的处理和稳定性监控仍在继续。[Microsoft 事后报告副本](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## 故障转移也需要接收上限

设计故障转移时，要检查**接收方当前还能处理多少额外请求**。例如，区域 A 要转移 1,000 个请求，而区域 B 在同一时间段内只有 300 个请求的余量，全量转移可能导致两个区域都发生故障。可以优先接收关键请求，对允许延迟的工作设置队列上限或暂时拒绝。过载时有意减少接收请求称为**负载削减（load shedding）**。[Microsoft Learn 过载控制指南](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/throttling)

恢复也遵循同一原则。本次故障中，服务器重新投入服务时收到积压的重连请求，又变得无响应。运维团队可以逐步将请求送回恢复的实例，同时观察连接成功率、延迟和队列。负载测试应在与生产环境同代的服务器上叠加**峰值流量、例行工作造成的容量下降、故障转移和重连**。分别测试可能遗漏这些条件同时出现时的问题。[Microsoft 事后报告副本](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## 聊天可以分开，决策记录应集中

据 Reuters 查看过的内部备忘录，响应人员交换了超过 11,000 条消息，分布在 11 个 Teams 聊天室。诊断数据散落在多个系统中，很难一眼看出哪些假设仍在调查、谁决定采取了什么措施。Microsoft 随后进入“Code Red”，优先防止故障重演并改进恢复。Reuters 报道的**全球一小时内恢复**是针对未来故障的内部目标。[GeekNews 介绍](https://news.hada.io/topic?id=37797) · [Reuters 文章转载](https://www.investing.com/news/stock-market-news/exclusivemicrosoft-declares-code-red-after-historic-outage-internal-memos-show-5048702)

即使各团队有独立调查渠道，也可以维护一份共享故障文档。开头列出**当前客户影响、已确认事实、正在调查的假设及负责人、最近措施及结果、下次通报时间**。例如，不只写“服务器已重启”，而写“重启后连接成功率短暂恢复，但重连请求涌入后再次下降”。接班人员据此可以判断是立即重复操作，还是先控制流量。也应检查访问故障文档的路径是否与待恢复服务有共同依赖。[Google SRE 的实时故障文档](https://sre.google/sre-book/managing-incidents/#live-incident-state-document)

下次故障演练可以从**峰值时一个区域容量下降**开始。确定剩余区域能接收多少请求、先缩减哪些功能，以及以什么速度将请求送回恢复的服务器。结束条件应超越服务器启动：用户能再次使用核心功能，积压请求也在减少。这样才能实际衡量恢复目标。

相关阅读 · [在 Spring Boot 4.2 中检查 RestClient 的 traceparent 传播（英文）](https://youdozi.github.io/en/posts/2026-11-22-spring-boot-4-2-restclient-traceparent/)
