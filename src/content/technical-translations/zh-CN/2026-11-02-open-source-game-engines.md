---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-02-open-source-game-engines",
  "routeSlug": "2026-11-02-open-source-game-engines",
  "kind": "post",
  "title": "开源游戏引擎比较：Godot、Bevy、Stride 与 O3DE",
  "description": "从团队工作流程、许可和目标平台限制比较 Godot、Bevy、Stride 与 O3DE，并提供可运行的 Godot 移动检查。",
  "categories": [
    "game-development"
  ],
  "tags": [
    "game-engine",
    "open-source",
    "godot",
    "bevy",
    "stride",
    "o3de"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-open-source-game-engines.md",
  "sourceSha256": "a83f90ac45031156dd23d82e78c770e9d3254849fbf67e9594455bc58c54e153",
  "draftSha256": "7f08864044527be22cdbbf6c87bff180cbec39ee90c690b2d7d4996921f0cdc4",
  "manifestPath": ".pipeline/technical-translations/batch-133/manifest.json",
  "manifestSha256": "012f8ab540d4cc0a5cef8d221664572be5fe6cfb38caebd3ef7cfc3c84c954a2",
  "publishedAt": "2026-11-02T04:33:37.064Z",
  "updatedAt": "2026-11-02T04:33:37.064Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 133,
    "approvedAt": "2026-11-02T04:33:37.064Z",
    "basis": "User explicitly requested writing and publishing a blog article using the game-engine review writing skill on 2026-11-02, with existing multilingual publication and standing blog PR merge authorization. Human approval denotes user publication authorization, not human/native linguistic review; language reviews are AI."
  }
}
---

**对于着手制作常规 2D 或 3D 游戏的小团队，Godot 是值得首先考虑的候选引擎。Bevy 适合愿意自行承担更多工具建设工作的 Rust 团队；采用 C# 工作流程的团队值得看看 Stride；能够维护较大规模 3D 内容与构建流水线的团队，则值得评估 O3DE。** 这些只是验证的起点，并非性能排名。

本文面向正在选择游戏引擎的开发者，比较依据是文档。2026年11月2日核查的版本参考为 Godot 4.7.2、Bevy 0.20、Stride 4.4 和 O3DE 26.05。下方可运行的示例只测试一个小型 Godot 移动函数，不能据此判断其他引擎的编辑器体验、渲染速度或导出可靠性。

## 我们在比较什么？

这四个项目都将自身称为游戏引擎。它们的工作流程各不相同：集成式可视化编辑器与代码驱动的 ECS 工作流程，需要团队自行组装的工具范围不同。框架或渲染库也可能合适，但比较时应将缺失的场景、资源和编辑工具计入团队必须承担的工作。

| 引擎及参考版本 | 开发工作流程 | 决定采用前首先要问的问题 |
| --- | --- | --- |
| [Godot 4.7.2](https://godotengine.org/download/archive/) | 场景／节点编辑器配合脚本 | 所选语言能否导出到实际目标平台？ |
| [Bevy 0.20](https://bevy.org/news/bevy-0-20/) | 以 ECS 为核心的 Rust 系统与组件 | 团队能否维护工具并处理 API 迁移？ |
| [Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/) | C# 与 Game Studio | 开发机器能否使用编辑器？ |
| [O3DE 26.05](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/) | 可扩展的 3D 编辑器与组件流水线 | 团队能否完成构建、资源导入并打包一个小场景？ |

下文的场景建议是根据这些工作流程推导出的，并非团队分别使用这些引擎发布游戏的经历。

## 哪款引擎适合团队的工作流程？

### Godot：从完整的制作循环开始

如果团队希望在同一个环境中编辑场景、附加行为并迭代，Godot 是合理的基准选项。其 [MIT 许可证](https://godotengine.org/license/)允许制作闭源游戏；分发引擎仍须附带相关的版权与许可声明。插件、字体、音乐和模型各有自己的条款。

尽早检查语言与平台的组合。[Godot 网页导出文档](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)目前指出，Godot 4 的 C# 项目无法导出到网页。因此，桌面 C# 原型不能作为可以交付浏览器版本的证据。对于主机平台，[Godot 的移植指南](https://godotengine.org/consoles/)说明了平台审批、官方 SDK，以及私有导出模板或第三方供应商的要求。开源引擎并不能免去这些流程。

### Bevy：选择 Rust 的同时承担工具建设责任

Bevy 是引擎，并非只有渲染器。其[入门介绍](https://bevy.org/learn/quick-start/introduction/)说明了 Rust、ECS，以及可选的 MIT 或 Apache 2.0 许可。介绍也提醒读者，API 版本发布可能带来破坏性变更，迁移可能很困难。

对于希望以系统和组件作为开发模型核心的团队，Bevy 因而值得关注。应将编辑器集成、资源迭代和版本迁移列为需要用团队项目实际验证的事项。仅仅熟悉 Rust，并不能说明制作循环会更快；并行 ECS 也不能证明某款游戏的帧耗时更短。

### Stride：区分 C# 支持与编辑器可用性

Stride 的 [FAQ](https://www.stride3d.net/faq/)说明，它采用 MIT 许可，且不收取引擎版税。其 C# 工作流程使其成为现有 .NET 团队值得考虑的候选。

[平台矩阵](https://doc.stride3d.net/latest/en/manual/platforms/index.html)区分了开发主机与游戏目标平台：Windows 提供完整的编辑器支持；Linux 和 macOS 在一定条件下支持构建及纯代码工作流程，而 Windows 以外的平台没有原生编辑器。[4.4 公告](https://www.stride3d.net/blog/announcing-stride-4-4/)介绍了非 Windows 构建的改进。不要据此声称所有平台都能使用相同的编辑器工作流程。

### O3DE：先评估流水线，再看演示效果

对于准备自行维护可扩展 3D 流水线的团队，O3DE 值得列入候选名单。其[许可文件](https://github.com/o3de/o3de/blob/2605.0/LICENSE.txt)规定默认采用 Apache 2.0，也可选择 MIT，并列出了另行许可的第三方组件。[下载页面](https://o3de.org/download/)列出了 Windows／Linux 软件包，以及较高的开发机器要求。这些是开发主机要求，不代表游戏导出目标平台的完整列表。

先尝试导入有代表性的资源、构建项目并打包场景。[26.05 发行说明](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/)将新粒子系统标为实验性功能，并不建议用于生产。某项功能出现在发行说明中，并不意味着它自动成为可用于生产的依赖。

## “免费”就意味着开源或制作零成本吗？

不是。能查看源码和购买价格为零，并不能说明项目采用开源许可证。例如，[Defold 目前将自身描述为源码可用](https://defold.com/open/)；应评估其具体许可证，而不是自动将它归入上述四款引擎。

引擎许可也不会替你支付主机移植、资源许可、托管、插件或维护的费用。决定之前，先明确哪些部分由引擎提供，哪些部分需要额外许可，哪些部分由团队构建。范围不明确时，不要估算总成本。

## 小型原型应该验证什么？

为入围的引擎设置相同的验收任务：加载一项有代表性的资源，实现一种交互，并为预期目标平台创建构建产物。记录环境搭建、反复编辑与运行时遇到的阻碍，以及任何无法满足的需求。这是一项建议的评估方法，并非本文已经执行的基准测试。

下面是一项可复现的检查：**无界面的 Godot 移动检查**。它接收位置、模拟方向和经过的秒数，将方向向量的长度限制为最大 1，再应用速度，并将所得点限制在矩形区域内。假定输入均为有限值，且经过的时间非负。这种限制并非障碍物碰撞、精灵尺寸处理或物理模拟。

![接收位置、方向与经过的时间，限制方向向量的长度，应用速度与时间，将点限制在边界内并返回新位置](/assets/diagrams/technical/zh-CN-2026-11-02-open-source-game-engines.svg)

图中展示了对 `advance` 的一次调用。下方的测试程序会重复调用并检查结果；它不读取键盘，也不渲染角色。[Vector2 参考文档](https://docs.godotengine.org/en/4.7/classes/class_vector2.html)说明了这些向量运算。这样可以将测试过的行为与编辑器生产力或游戏性能方面的主张区分开来。

标准 Godot 4.7.2 编辑器二进制文件可通过 `godot` 调用时，将 `project.godot` 和 `movement.gd` 保存到同一目录。安装引擎后，运行脚本无需场景、外部资源、软件包或网络访问。

`project.godot`：

```ini
config_version=5
```

`movement.gd`：

```gdscript
extends SceneTree

const SPEED := 120.0
const LIMIT := Vector2(640.0, 360.0)

func advance(pos: Vector2, direction: Vector2, delta: float) -> Vector2:
    var bounded := direction.limit_length(1.0)
    var next := pos + bounded * SPEED * delta
    return next.clamp(Vector2.ZERO, LIMIT)

func _initialize() -> void:
    var cases := [
        [Vector2(100, 100), Vector2.ZERO, 0.5, Vector2(100, 100)],
        [Vector2(100, 100), Vector2.RIGHT, 0.5, Vector2(160, 100)],
        [Vector2.ZERO, Vector2(1, 1), 1.0, Vector2(84.852814, 84.852814)],
        [Vector2.ZERO, Vector2(0.5, 0), 1.0, Vector2(60, 0)],
        [Vector2(639, 100), Vector2.RIGHT, 1.0, Vector2(640, 100)],
        [Vector2(5, 100), Vector2.LEFT, 1.0, Vector2(0, 100)],
        [Vector2(100, 359), Vector2.DOWN, 1.0, Vector2(100, 360)],
        [Vector2(100, 100), Vector2.RIGHT, 0.0, Vector2(100, 100)],
    ]
    for sample in cases:
        var actual := advance(sample[0], sample[1], sample[2])
        if not actual.is_equal_approx(sample[3]):
            push_error("movement mismatch")
            quit(1)
            return
    var split := advance(advance(Vector2(100, 100), Vector2.RIGHT, 0.25), Vector2.RIGHT, 0.25)
    if not split.is_equal_approx(advance(Vector2(100, 100), Vector2.RIGHT, 0.5)):
        push_error("time-step mismatch")
        quit(1)
        return
    print("movement cases=9")
    quit(0)
```

在该目录中通过 [Godot 命令行接口](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html)运行。在 macOS 上，如果安装的应用程序包不在 `PATH` 中，将 `godot` 替换为其 `Godot.app/Contents/MacOS/Godot` 路径。

```sh
godot --headless --no-header --path . --script movement.gd --quit-after 1
```

该示例已在 macOS 上使用 Godot 4.7.2 本地执行。输出如下：

```text
movement cases=9
```

这些检查覆盖了无输入、水平和对角线移动、未达到最大长度的方向输入、上下界、经过时间为零，以及远离边界时将时间步拆分的情况。它们没有验证渲染、目标设备导出、障碍物、网络或引擎间的性能差异。

## 最终应该如何选择？

选择能满足游戏所需工作流程和目标平台构建要求，且维护负担在团队可接受范围内的候选引擎。如果优先考虑可视化编辑循环，就先用 Godot 制作原型。如果团队明确希望掌握 Rust／ECS 工具体系，就测试 Bevy 的工具建设与迁移成本。对于 C# 团队，在实际使用的编辑器主机上测试 Stride。对于较大规模的 3D 流水线，在依赖演示中的亮眼功能之前，先验证 O3DE 的资源与构建循环。

接下来有用的产物是小型目标设备构建和未满足需求清单，而不是通用的引擎排行榜。将这些决策依据保存在项目旁，便于在引擎升级时按相同的行为进行评估。
