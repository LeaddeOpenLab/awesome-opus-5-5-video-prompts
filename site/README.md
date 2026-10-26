# Leadde Open Lab · GitHub Pages

## Catalog and template updates

The homepage now includes Selected / Latest / All browsing, seven use-case filters,
full-library search and batches of 24 cards. Category counts cover the complete
library; records may appear in multiple categories. Search covers all records.

`site/catalog.py` reads published records from `data/library/` with matching
`prompts/<id>.md` files. Cards use existing covers, author, purpose, tools and
prompt status. Latest means records stored on the date in `data/latest-update.json`.
Non-selected cases link to the existing GitHub prompt rather than generating new
detail pages. Homepage picks now include three recent additions, with fifteen detail pages retained in total.

Three editable templates reuse their existing posters and MP4 previews, linking
to their GitHub directories and Chinese guides. Pages rebuilds also watch template,
category, cover and latest-update changes. Updates pushed with GITHUB_TOKEN still
need an explicit deployment trigger, as described below.

这是 `awesome-opus-5-5-video-prompts` 的轻量内容站。沿用 Leadde 的紫色、Logo、白底和深灰文字，以作品和使用信息为主。首页、三个专题、十五个案例共 19 个可索引页面；另有 404 页面。

## 本地预览

在仓库根目录运行：

```sh
python3 site/build.py
python3 site/check.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory _site
```

浏览器打开 `http://127.0.0.1:4173/`。构建仅需 Python 标准库，不需要 npm、数据库或 API Key。

## 发布到 GitHub Pages

1. 将本次新增的 `site/`、`.github/workflows/pages.yml`、`.gitignore` 提交到 **LeaddeOpenLab/awesome-opus-5-5-video-prompts** 的 main 分支。本地目录名 `opus-prompt-site` 不代表另一个远程仓库。
2. 仓库 → Settings → Pages → Build and deployment → Source，选择 **GitHub Actions**。
3. Actions → Deploy prompt collection to GitHub Pages → Run workflow。
4. 部署成功后，以工作流返回的网址为准。默认地址应为：
   `https://leaddeopenlab.github.io/awesome-opus-5-5-video-prompts/`
5. 可以在仓库 About 的 Website 字段和 README 中加入该地址。README 目前由其他流程维护，发布前未自动改动，避免上线前出现无效入口。

工作流只发布 `_site/`，不会把原始数据、维护记录或整个仓库发布成网站。推送 `site/` 或 `data/library/` 后会重新构建。用 GitHub 默认 GITHUB_TOKEN 推送的自动化更新通常不会触发下一个 push 工作流；如你们的数据更新使用该机制，更新后手动运行 Pages 工作流，或由更新流程显式触发部署。

发布状态以 GitHub Actions 中最近一次 Pages 部署结果为准。

## Google Search Console

1. 网站发布后，在 Search Console 添加 **网址前缀** 资源，输入完整的 Pages 网站地址（包含仓库路径和末尾 `/`）。
2. 选择 HTML 标记验证，复制 `content` 属性中的验证值。
3. 二选一：
   - 在 GitHub Settings → Secrets and variables → Actions → Variables 中添加 `GOOGLE_SITE_VERIFICATION`，然后手动运行 Pages 工作流；或
   - 填入 `site/site.json` 的 `google_site_verification`，提交后自动部署。
4. 部署后回到 Google 点击验证，保留验证值。
5. 提交 `sitemap.xml`，检查首页和案例页，然后请求索引。

没有填入验证码时不会输出伪造的验证标签。验证和提交不保证收录或排名。网站数据不会包含既有 GitHub 仓库搜索历史。

GitHub 项目站位于子路径，子路径下的 robots.txt 无法控制域名根目录的抓取规则，因此不生成一个无效的项目级 robots.txt；通过 Search Console 提交 sitemap 即可。

### 站点地图策略（2026-10-26）

- 主文件仍为 `sitemap.xml`。构建同时从同一页面列表生成 UTF-8 `sitemap.txt`，每行一个完整的规范网址，无标题和注释。TXT 仅作为 XML 持续无法抓取时的一次备用提交测试；Google 不偏好某种格式，换格式不保证解决抓取问题。
- 只包含本站希望收录的首页、专题、精选案例和教程，不包含 404、外站仓库地址或媒体文件。当前只有 20 个页面，无需拆分 sitemap 或增加 sitemap index。
- 继续省略无法可靠确定的 `lastmod`；不要拿构建时间、采集时间冒充页面实质更新时间。不要添加 Google 忽略的 `priority`、`changefreq`。
- 发布后先确认 TXT 网址返回 200、内容为一行一个 URL，再在当前网址前缀资源的“站点地图”输入框填写 `sitemap.txt`（前缀已包含仓库路径）。保留原 XML 记录用于对照，不反复改名或每日重复提交。
- sitemap 通过“站点地图”报告提交，不给 XML/TXT 文件本身“请求编入索引”。网址检查中的实时测试仅用于诊断抓取，不代表正式 sitemap 处理成功。
- 重点 HTML 内页可以独立请求编入索引，无需等待 sitemap 成功；保留正常可抓取的站内链接。手动请求成功不保证最终收录。
- 分开观察：sitemap 的上次读取时间、状态与已发现网页数；HTML 页的上次抓取时间、索引状态与规范网址。TXT 若也失败且实时测试通过，保留具体错误反馈给 Search Console，不据此重构站点或迁移域名。
- 若未来能维护 `https://leaddeopenlab.github.io/robots.txt`，可在域名根目录声明完整 sitemap URL；本项目子目录下添加 robots.txt 无效，当前不为此新建根站。

官方依据：[构建与提交 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)、[站点地图报告与抓取排错](https://support.google.com/webmasters/answer/7451001)、[请求重新抓取](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)。

## 内容维护

- `site/selection.json`：十五个详情案例（首页选取九个）、页面路径、编辑后的标题、简短介绍和使用建议。
- `data/library/<id>.json`：原作者、原文提示词、来源和模型说明。构建时直接读取，不另建一份提示词数据库。
- `site/build.py`：生成完整静态 HTML、独立 metadata、canonical、Open Graph、WebPage/CollectionPage 结构化数据与 sitemap。
- `site/assets/site.css`、`site.js`：响应式样式、筛选、搜索、复制提示词和预览弹窗。
- `site/assets/posters/`、`previews/`：从仓库现有 GIF 与本地已有的原作者视频中抽取的封面和静音 MP4 短预览，不代表新复现成果。资产总量约 2.6 MB，视频按需加载。

新增案例时增加 selection 记录并准备同 ID 的 jpg 封面与 mp4 预览。构建会读取最新提示词内容。媒体更换时需同步更新预览资产。

现有九个案例均明确标注未由本站独立复现。使用建议与原作者提示词分开展示；英文翻译、工具不明确、工作区上下文缺失等信息保留在案例页。没有编造成功率、制作时长、用户数或 Star 数。

站点地址变更时更新 `site/site.json` 的 `url`，再构建。默认使用 GitHub Pages 项目路径，不需要自有域名。

## 已做的验证

`python3 site/check.py` 检查生成页面、元数据、站内链接、锚点、静态资产和 sitemap。

本地另进行了隔离无头浏览器检查：桌面/手机布局、筛选、搜索空状态、预览播放与关闭、复制原文、无 JavaScript 正文可读。截图位于 `site/qa/`，不随站点部署。

## 语言切换

导航栏提供 English / 简中，首次访问默认英文，手动选择后会在当前浏览器中记住语言。`site/zh-CN.json` 保存简中文案，构建时与现有英文内容生成翻译表。首页、专题、案例和操作提示均可切换，作者提示词保留现有英文文本，复制内容不变。静态 HTML 和默认 SEO 元数据仍为英文，不新增语言网址。

## 已添加 HTML 文件验证

Google 提供的 `google9ddda4d9c22709a6.html` 保存在 `site/public/`，每次构建会原样复制到网站根目录。Search Console 中使用 HTML 文件验证即可，不必再填写 meta 验证值。验证成功后保留此文件。

## 展示与行为统计

卡片常驻播放入口，预览弹窗可直接复制原始提示词；复制权限不可用时显示并选中文本，供手动复制。首屏精选静音循环预览，离开可视区域、切换后台或打开弹窗时暂停，也可手动暂停；系统设置减少动态效果时默认不自动播放。

在 `site/site.json` 中填写 `ga_measurement_id`，或在 GitHub Actions Variables 中设置 `GA_MEASUREMENT_ID`，重新构建部署后启用 GA4。未配置时只在当前页面的 `window.dataLayer` 中排队事件，不向统计服务器发送数据，也不会汇总访客数据。

事件：`preview_play`（实际开始播放，每页面同一案例同一位置只计一次）、`prompt_copy`（剪贴板写入成功）、`github_click`、`leadde_click`。事件包含位置 `placement`，播放和复制包含 `prompt_id`，首屏播放标注 `autoplay`。不发送提示词正文或搜索输入。可以在 GA4 DebugView / 实时报告验证接收；需要按案例和位置分析时，将对应参数注册为自定义维度。

作品区第一张主推卡进入可视区域后静音循环播放，可手动暂停；其他卡片在支持鼠标悬停的设备上悬停播放、移出暂停并恢复封面。移出可视区域、切换后台、筛选隐藏或打开弹窗时暂停。视频按需加载；触屏仍使用点击预览，减少动态效果设置下默认不自动播放。播放统计位置新增 `spotlight` 和 `hover`。

## 2026-10-19：精选与仓库导流

首页首屏及前三个精选更新为东京雨夜、15 秒 Showreel、像素巫师；魔方原帖不可用后已从精选移除，原详情页仍保留。旧详情页保持原网址；新页面有独立标题、canonical 和 sitemap 条目。新增 MP4 复用仓库 GIF 短预览，保留原作者比较画面与标注，不代表完整视频或本站复现。README 前三个精选与本地 `prompt-pipeline/src/local-admin/curated-layout.ts` 生成配置同步更新；自动发布流程应使用更新后的生成配置。

`github_click` 沿用原事件名，新增事件参数：

| 参数 | 用途 |
| --- | --- |
| `repo_target` | `collection` 为本仓库，`external` 为其他 GitHub 仓库 |
| `prompt_id` | 作品 ID；模板入口使用模板 slug；全站入口无此参数 |
| `placement` | `hero-prompt`、`selected-card`、`preview-prompt`、`detail-prompt`、`detail-source`、`category-library`、`catalog-prompt`、`template-get` 等位置 |
| `link_type` | `prompt`、`category`、`template`、`repository`、`star`；`star` 仅表示点击 Star 引导，不表示成功收藏 |

上线后在 GA4 管理 → 自定义定义，将以上四个参数注册为事件范围的自定义维度（已有的无需重复创建）。本地验证只确认 dataLayer 事件，不等于 GA4 已接收或自定义维度已配置。

最小探索报表：筛选 `event_name = github_click` 且 `repo_target = collection`；按「会话来源 / 媒介」查看总用户数、事件数，再用 `prompt_id` 和 `placement` 分解。用 GA4 内置会话来源，不新增自制来源追踪。对比全体与排除 `github.com / referral` 的用户，后者只作站外来源导流近似值，不能声称首次访问仓库。direct 仍是来源未知。GitHub Insights 的独立访客数单独观察，不能与站外点击做精确用户匹配。

复制率与播放另看 `prompt_copy`、`preview_play`；自动播放（hero/spotlight）、悬停播放（hover）和主动预览（preview/detail）分别分析。


## 2026-10-19：ORBIT 实操教程

新增 `/tutorials/codex-product-launch-video/`，首页首屏文字链接及精选区前的卡片均直接进入教程。原有精选保持不变。`site/orbit.py` 在正式构建中生成页面、编辑器和 ZIP；正文在 `site/tutorials/`，中英文及样式在 `site/assets/orbit*`，源代码在 `templates/orbit-launch-15s/`。

教程有独立 title、description、canonical、分享封面、WebPage / BreadcrumbList / VideoObject 结构化数据，并加入 sitemap（现共 20 个可索引页面）。编辑器明确 noindex，不加入 sitemap；检查器仍验证编辑器的元数据与资源链接。`orbit.json` 中的发布日期固定保存，不随每次构建刷新。

ZIP 只包含明确列出的源码、说明、许可证和中英文复现提示词，不包含本地对话、QA 输出或开发机路径。教程明确区分 Codex 改作、虚构产品和复现提示词；本地检查涵盖播放、复制、下载、语言切换和手机布局。
