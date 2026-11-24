---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-24-github-pages-ads-guide",
  "routeSlug": "2026-11-24-github-pages-ads-guide",
  "kind": "post",
  "title": "在 GitHub Pages 技术博客中投放广告：从选择服务到安装 AdSense",
  "description": "选择广告服务，在 GitHub Pages 上设置 AdSense 和根目录 ads.txt，并检查审核与广告投放状态。",
  "categories": [
    "tips"
  ],
  "tags": [
    "github-pages",
    "adsense",
    "ads-txt"
  ],
  "sourcePath": "src/content/posts/en/2026-11-24-github-pages-ads-guide.md",
  "sourceSha256": "884b5c639b2345ac6daac6b307db2cd0ec22e80801c8d5d2d5860b4ba12356d8",
  "draftSha256": "bad826be2122e517f91c27d12efe802b12b31cebc6247a29e9acddf8bd7cc035",
  "manifestPath": ".pipeline/technical-translations/batch-190/manifest.json",
  "manifestSha256": "6b40a455d4e018ed7edaefaa33a3094c5c1475c70d97ffdc7106618f6fa84d3f",
  "publishedAt": "2026-11-24T08:55:29.701Z",
  "updatedAt": "2026-11-24T08:55:29.701Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 193,
    "approvedAt": "2026-11-24T08:55:29.701Z",
    "basis": "Owner requested publication in eight languages; translations self-reviewed without independent or native-speaker review."
  }
}
---

如果你在 `username.github.io` 运营技术博客，可以先考虑 Google AdSense。如果网站有稳定的开发者读者，Carbon Ads 和 EthicalAds 也是候选。申请前先确认自己能否发布 `https://username.github.io/ads.txt`；项目地址为 `username.github.io/blog/` 时尤其需要注意。

GitHub 通常不禁止以内容为主的网站展示广告。不过，GitHub Pages 限制将其用作经营在线业务、电子商务或商业 SaaS 的免费托管服务。在技术博客上添加广告时，应同时查看这两项政策。[GitHub 广告政策](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies#10-advertising-on-github) · [GitHub Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

## 选择哪种广告服务？

| 服务 | 适合的网站 | 申请 |
| --- | --- | --- |
| **Google AdSense** | 首次在个人博客上放置广告，并希望选择自动或手动布局 | [开始使用 AdSense](https://adsense.google.com/start/) |
| **Carbon Ads** | 面向开发者和设计师的文章、文档及工具。每月 10,000 次页面浏览量起接受审核，不允许同时使用其他广告网络。 | [申请 Carbon Ads](https://www.carbonads.net/join?_hsmi=83378591) |
| **EthicalAds** | 每月页面浏览量至少 50,000 次的开发者网站，能够在不妨碍阅读的位置放置一处广告 | [EthicalAds 发布商指南](https://www.ethicalads.io/publisher-guide/) |

先决定广告放在哪里。例如，对于代码示例较多的博客，可以先在文章下方手动放置一处 AdSense 广告，再在手机上查看。AdSense 提供由你决定位置的 **广告单元** 和由 Google 决定位置的 **自动广告**。EthicalAds 另有布局要求：广告应在桌面和移动设备的首屏中可见；如果移动端无法满足，可以关闭移动端广告。[AdSense 广告设置](https://support.google.com/adsense/answer/7037624)

![AdSense 流程：添加代码，在根目录发布 ads.txt，检查公开网址，然后请求审核。](/assets/diagrams/technical/zh-CN-2026-11-24-github-pages-ads-guide.svg)

此图概括设置和请求审核的步骤；实际广告投放需要单独检查。

## 1. 注册 AdSense 并添加网站

使用 Google 账号注册 AdSense，填写付款国家和付款信息。在 **网站 → 新网站** 中添加 `https://username.github.io`。Public Suffix List 包含 `github.io`，AdSense 说明可以将该列表中平台的子域名添加为网站。之后需要验证所有权并审核网站。[创建 AdSense 账号](https://support.google.com/adsense/answer/7402253) · [AdSense 网站标准](https://support.google.com/adsense/answer/12170421) · [Public Suffix List](https://publicsuffix.org/list/public_suffix_list.dat)

确认网址：GitHub Pages 用户站点位于 `username.github.io/`，项目站点通常位于 `username.github.io/blog/`。将 `ads.txt` 放进项目构建产物，可能会发布到 `/blog/ads.txt`。Google 从主机根目录 `/ads.txt` 开始查找，因此应通过用户站点发布根目录文件，或从博客所用自定义域名的根目录提供文件。[GitHub Pages 站点类型](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#types-of-github-pages-sites) · [Google ads.txt 抓取说明](https://support.google.com/adsense/answer/7679060)

## 2. 在共用 `<head>` 放一段代码，在根目录放一个 `ads.txt`

AdSense 提供代码片段、`ads.txt` 和元标记等所有权验证方式。如果选择代码片段，将控制台提供的代码放进共用布局的 `<head>`。下面仅为格式示例；实际部署时使用从自己账号复制的代码。[连接网站](https://support.google.com/adsense/answer/7584263)

```html
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0000000000000000"
  crossorigin="anonymous"></script>
```

将控制台提供的行复制到 `ads.txt`。该文件公开有权销售网站广告库存的账号。如果已有其他销售者条目，请保留原有行并追加新行。

```text
google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0
```

对于使用 Astro 的用户站点，将文件放在 `public/ads.txt`；Astro 会将 `public/` 中的文件复制到构建结果。部署后要检查公开网址能否访问，而不只是检查仓库。[Astro 的 `public/` 目录](https://docs.astro.build/en/guides/images/#src-vs-public) · [Google ads.txt 指南](https://support.google.com/adsense/answer/12171612)

```bash
curl -fsSL https://username.github.io/ads.txt
```

预期输出是上面的示例销售者行。真实网站应返回其账号的发布商 ID。`username` 地址仅作示例，这不是实际执行结果。

同一主机上的多语言博客只需一个根目录文件，不必分别在 `/ko/` 和 `/en/` 下创建。检查每种语言的代表文章最终 HTML 中是否恰好有一个共用加载脚本。

## 3. 分别检查部署、审核和广告投放

部署文件和代码后，在 AdSense 中验证所有权并请求网站审核。网站状态 **`Ready`** 表示网站已准备好展示广告；ads.txt 状态 **`Authorized`** 表示 Google 在文件中找到了发布商 ID。如果公开网址可访问但控制台仍显示 `Not found`，请检查更改是否发生在上次抓取之后。路径和内容正确时，可以使用 **检查更新** 请求重新检查。[网站状态](https://support.google.com/adsense/answer/12170222) · [ads.txt 状态](https://support.google.com/adsense/answer/12171612)

启用广告前，应在隐私政策中说明为广告收集或共享的信息及 Cookie 等技术。向欧洲经济区（EEA）、英国和瑞士的访客提供个性化广告，需要使用与 IAB Transparency and Consent Framework（TCF）集成的 Google 认证同意管理平台（CMP）。AdSense **隐私与消息**中的欧洲法规消息也是一种选择。[Google 发布商隐私政策](https://support.google.com/adsense/answer/10502938) · [Google CMP 要求](https://support.google.com/adsense/answer/13554116)

审核完成后，使用自动广告预览或手动广告单元检查布局。在手机上确认广告没有遮住目录、代码复制按钮或语言切换菜单。不要通过点击自己的广告进行测试；请使用预览和控制台报告。[自动广告预览](https://support.google.com/adsense/answer/9261307) · [无效流量](https://support.google.com/adsense/answer/16737)

已检查 `youdozi.github.io` 公开根目录的 `ads.txt` 和韩语首页 HTML 中的一段 AdSense 脚本。检查范围仅限公开文件和 HTML；账号审核状态与实际广告投放需要另行确认。[公开 ads.txt](https://youdozi.github.io/ads.txt) · [韩语首页](https://youdozi.github.io/ko/)
