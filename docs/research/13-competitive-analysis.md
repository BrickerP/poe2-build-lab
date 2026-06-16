# Finding 13: Competitive analysis — PoE2 build decision assistant

> **PoE2 Build Decision Assistant — 竞品分析报告**
>
> 基于 `/Users/yupeng/Downloads/money/docs/research/` 全部 13 份 Markdown 研究卡片 + 代码库扫描。研究日期：2026-06-16，游戏版本：0.5 Return of the Ancients（含 0.5.2 hotfix 语境）。

---

## A. 竞品地图

| 竞品类别 | 代表 | 做得好的 | 做得不好 / 空白 |
|---------|------|---------|----------------|
| **大型攻略站** | Maxroll | 深度 build 指南、升级/装备路线、视频联动、league starter 聚合、内容更新快 | 偏「推荐哪个 build」，缺少结构化属性校验、gear swap 断技能预警、trade filter 生成；patch 有效性依赖人工维护 |
| **Build Planner 平台** | Mobalytics | 有 PoE2 Build Planner + `.build` 导出（`03-build-planner-build-files.md`）；endgame 概览（`08-endgame-progression-rewards.md`） | 偏 planner/导入导出，不是「决策助手」；trust/budget/complexity 标签弱；无 slot 级 affix 优先级 + trade handoff 闭环 |
| **天梯/经济** | PoE Ninja | PoE1 领域强：价格、meta、角色快照 | **PoE2 适用性有限**；研究文档未将其列为 PoE2 build 决策核心来源；不是 build-to-gear 决策链工具 |
| **数据/wiki 库** | PoE2DB、PoE2 Wiki/Fandom | PoE2DB：modifier/base/gem 全量分类（`06-gear-affixes-crafting.md`）；Wiki：属性机制说明（`05-attributes-stat-starvation.md`） | 纯参考查询，无 build 上下文；不回答「这个 build 该优先哪个 slot 的哪个词缀」 |
| **官方工具** | GGG Build Planner + Trade | 官方 `.build` schema、`inventory_slots` 词缀优先级 hint（`03`、`06`）；官方 trade/bulk exchange（`09`） | **游戏内编辑 build 尚不支持**（`03`）；trade UI 需 JS + 登录，无「从 build 需求生成 filter」；无 trust/budget 层 |
| **社区/创作者** | Reddit r/pathofexile2builds、YouTube、论坛 | 真实痛点发现、build 索引聚合 Maxroll/Mobalytics/Reddit/YouTube（`04`）；build review 文化 | 索引**自承 under construction + bait 风险**（`04`）；信息碎片化、无机器可读 build 定义、patch 标注不一致 |
| **辅助工具** | Craft of Exile POE2、Path of Building Community、Filterblade | 社区书签推荐（`10-data-source-tooling.md`）：craft 模拟、PoB 计算、loot filter | 各管一段（craft / DPS / filter），**不与 build 卡片、属性、trade 串联** |
| **你们现有站点** | PoE2 Build Lab（静态 MVP） | 已有 beginner checklist、patch 标注意识（`01-site-capability-gap.md`） | 无 JSON build 层、无 calculator、无 `.build` export、无 trade handoff |

**核心结论（来自 `README.md` expert model）：**

竞品普遍只覆盖链条中的一段，而 PoE2 build 是强耦合系统：

`class/ascendancy → passives → skills/spirit → attributes → gear slots/affixes → defenses → budget/trade → patch validity → .build handoff`

没有任何单一竞品完整建模这条链。

---

## B. 可以 Copy 的部分

| 模式/功能 | 来源 | 具体做法 | 采纳理由 |
|----------|------|---------|---------|
| **Build Card 元数据字段** | `04-community-build-discovery-trust.md` | `patch`、`budget`、`complexity`、`gear_dependency`、`source`、`risk`、`import_file: yes/no` | 直接回应「这是 bait 吗？」「预算够吗？」——Reddit 索引有需求但无结构化实现 |
| **Trust rubric 评分维度** | `04` | source type、patch verified date、budget floor、controller/HC/SSF/trade viability、known failure mode | 社区索引自承 PoE2 知识弱于 PoE1，trust 层是差异化核心 |
| **`.build` 下载 + 安装说明** | `03-build-planner-build-files.md` | Download `.build`、Windows/SteamOS 路径、JSON 校验后再发布 | Reddit 当前高需求话题；官方 schema 已就绪；Mobalytics 已有 export 但需求仍旺盛 |
| **`inventory_slots` 词缀优先级 hint** | `03`、`06` | 每 slot：`base` + ranked `priority` + `budget_note`（campaign vs maps） | 官方 schema 原生支持 hover text；比 prose「换更好装备」可执行 |
| **Mobalytics 式 import/export 流** | `03`（Reddit: Mobalytics Build Planner Export） | 页面顶部 CTA：Download `.build` / Copy JSON；说明 in-game editing 不可用 | 降低从「读攻略」到「进游戏」的摩擦 |
| **Maxroll 式 gear progression 分段** | `06`、`07`（Ice Strike Monk gear progression 等 Reddit 信号） | 按 campaign / early maps / red maps / pinnacle 分段列出 slot 升级顺序 | 玩家问的是「下一步买什么」，不是「终局 BiS 是什么」 |
| **Beginner defense checklist** | 现有 `tools/beginner-build-checklist.html` + `07` | 可交互 checklist + per-build 量化目标（life/ES/resist/spirit） | 站点已有雏形；`07` 指出「为什么死」需要 diagnostic tree |
| **PoE2DB 式 slot/modifier 分类** | `06`、`10` | gear module 按 slot → base type → top 3 affix 组织 | 数据面已验证可行；用 transformed guidance + attribution，不 bulk clone（`10` source risk） |
| **Trade handoff（filter recipe，非标价）** | `09-trade-price-economy.md` | budget tier 分档 + 「该搜什么词缀、可忽略什么 luxury」+ 链到 official trade | Reddit 明确不做 price check；volatile 价格不适合承诺 |
| **Patch 元数据可见性** | `02-current-game-context.md` | 每页：`patch_version`、`last_reviewed`、`known_broken_by_patch`、未复测 warning | 0.5 时代 hotfix 频繁，静态 guide 快速失效是 universal pain |
| **Quick answer / notice 块** | 现有 `guides/beginner-guide.html` | 页面顶部一句话结论 + 下方展开 | 降低新手 cognitive load；Maxroll/Mobalytics 同类 pattern |
| **Research → page 工作流** | `11-social-source-strategy.md`、`12-product-roadmap.md` | Reddit 发现 pain → research card → 长尾 page/tool | 可持续内容引擎，避免 AI slop |

**不应 Copy 的：**

- PoE Ninja 式「固定价格 / 角色排行」——PoE2 经济不稳定，且与 build 决策弱相关（`09`）
- PoE2DB 式 raw database 镜像——AdSense/SEO 风险（`10`）
- 「Best Builds」纯列表页——`04` 表明用户真正问的是 trust + viability，不是排名

---

## C. 竞品无法满足的遗留痛点

### 1. 新手痛点

| 痛点 | 竞品谁没做好 | 为什么失败 | 我们可怎么做 |
|------|-------------|-----------|-------------|
| **「我能装备/用这个吗？」** | Wiki 只解释机制；Maxroll/Mobalytics 很少算 Str/Dex/Int 缺口 | 属性是 cross-cutting concern，散落在 tree/gear/gem 三处（`05`） | **Attribute Budget Calculator**：输入 tree + gems + gear → 输出缺口 + 哪个 slot 该补属性 |
| **换装备后技能 silently break** | 无竞品做 gear-swap validator | weapon set、gem requirement 交互复杂（`05` Reddit 信号） | **Gear swap 预警**：「换此 item 会 break 这些 skills」 |
| **「这个 build 是 bait 吗？」** | Reddit 索引自承 bait 可能混入（`04`）；YouTube 偏 showcase | 无统一 trust rubric；budget/complexity 不可比较 | **Build Cards** 带 budget/complexity/gear_dependency/risk 标签 + proof 字段 |
| **「generic 换更好装备」不够** | 大部分 guide 是 prose | 物品价值依赖 slot/base/affix/build scaling（`06`） | **Per-slot gear module**：base + top 3 affix + budget tier + 可妥协项 |
| **「为什么我一碰就死？」** | Guide 讲 defense 概念，不给 per-build 量化目标 | 生存问题是 layered diagnostic（`07`） | **Defense Checklist Calculator**：resist gap / life-ES / spirit / recovery / 该避 map mod |
| **Spirit 来源不透明** | Reddit ELI5 帖频繁（`06`） | spirit 来自多源，guide 很少 slot 级拆解 | Build Card 标注 spirit budget + 哪些 slot/aura 贡献 |
| **`.build` 怎么用？** | 官方文档偏 dev；社区帖分散（`03`） | 游戏内编辑未开放，外部工具碎片化 | 一站式：Download + 安装路径 + 校验过的 JSON |

### 2. 老玩家痛点

| 痛点 | 竞品谁没做好 | 为什么失败 | 我们可怎么做 |
|------|-------------|-----------|-------------|
| **Patch 后 build 是否仍 valid** | Maxroll/Mobalytics 有人工更新，但无 structured `known_broken_by_patch` | 0.5.2 持续改 Atlas/Delirium/ES（`02`、`07`） | 每 Build Card 强制 patch metadata + changelog diff |
| **Trade 搜索不知道怎么 filter** | 官方 trade 功能完整但无 build 上下文（`09`） | build 站刻意不做 price check（Reddit 规则） | **Trade Handoff**：从 slot priority 生成 filter recipe + budget tier |
| **Affix 优先级随 budget 变化** | PoE2DB 有全量 mod，无 build+budget 语境 | DB 是 lookup，不是 decision | 「campaign 可忽略 X，red maps 前必须 Y」 |
| **Endgame progression 与 build 脱节** | Mobalytics 有 endgame overview（`08`），但与具体 build 的 defense/gear 假设未绑定 | 内容是 hub，不是 per-build 决策 | Build Card 标注 content stage viability（campaign/maps/pinnacle） |
| **工具链断裂** | PoB / Craft of Exile / Filterblade / Trade 各管一段（`10`） | 无统一 build 对象串联 | 以 `data/builds/*.json` 为 hub，各 module 读同一 build 定义 |

### 3. 工具/数据链断裂

| 断裂点 | 现状 | 机会 |
|--------|------|------|
| **Guide prose ↔ 机器可读 build** | 当前站点仅 static HTML（`01`） | `builds/*.json` → 渲染 guide + 导出 `.build`（`12` Phase 2-3） |
| **Passive tree ↔ 官方 export** | GGG `poe2-skilltree-export` 5151 nodes 可静态 ingest（`10`） | 无需 backend 即可做 passive milestone 展示 |
| **Modifier 数据 ↔ build 语境** | PoE2DB 有 depth，guide 无 slot binding（`06`） | Transformed slot guide + provenance，非 raw scrape |
| **Build requirements ↔ trade filters** | 官方 trade 与 build 站无 bridge（`09`） | Filter recipe handoff，明确不做 volatile 标价 |
| **Community discovery ↔ trust** | Reddit 聚合链接但不 vet（`04`） | Build Cards 作为 curated + rubric 层，可索引社区 build 但标注 source/risk |
| **Patch notes ↔ build validity** | X/forum 更新快，guide 更新慢（`11`） | `last_reviewed` + 未复测 warning 自动化 workflow |

---

## D. 差异化优先级建议（MVP）

按 **影响 × 可行性** 排序（对齐 `12-product-roadmap.md` Phase 2-5）：

| 优先级 | 机会 | 影响 | 可行性 | MVP 范围 |
|--------|------|------|--------|---------|
| **1** | **Build Cards + patch/trust 元数据** | 高 — 直接解决 #1 新手问题「选哪个、是否 bait、是否过期」 | 高 — 纯 JSON + 静态渲染，无需复杂计算 | Phase 2：`data/builds/*.json` + trust rubric 字段（`04` yaml 模板） |
| **2** | **`.build` export + inventory_slots hints** | 高 — Reddit 明确 demand（`03`）；Mobalytics 有但非独家 | 中高 — 需 schema validation + 官方 passive/skill ID | Phase 3：从 Build Card 生成校验 JSON + 安装说明 |
| **3** | **Attribute Budget + gear swap 预警** | 高 — 竞品空白最明显（`05`）；强决策助手属性 | 中 — 需 gem/base requirement 数据，但可 client-side | Phase 4：静态 calculator，MVP 可先做「planned loadout deficit」 |
| **4** | **Per-slot gear priority + budget tier** | 中高 — 解决「买什么」（`06`） | 高 — 结构化 YAML，可人工 authored | 嵌入 Build Card，campaign/maps 两档即可 |
| **5** | **Trade filter handoff（非标价）** | 中 — 老玩家价值高（`09`） | 中 — 官方 trade deep link 能力待验证；MVP 可先「filter recipe 文本 + 链接」 | Phase 5：filter recipe + budget tier warning |

**建议 MVP 不做 / 后置：**

- PoE Ninja 式价格追踪 — 与产品定位冲突（`09`）
- 完整 PoB 级 DPS 模拟 — 复杂度高，PoB Community 已存在（`10`）
- Endgame Hub 全量 — 有价值（`08`）但偏离「build decision assistant」核心，可作为 SEO 长尾后置
- Bulk PoE2DB 镜像 — 法律/SEO 风险（`10`）

---

## 诚实评估：竞品已经做得不错的地方

避免 oversell 不存在 gap 的领域：

1. **Maxroll / Mobalytics 的 build 指南深度** — 已有 league starter、 leveling、 gearing 段落；我们不是要再做一份 prose guide。
2. **Mobalytics `.build` export** — 已存在（`03` Reddit 讨论）；我们的优势是 export **+** trust/attribute/gear/trade 闭环，而非 export 本身。
3. **官方 Build Planner schema** — GGG 已定义 `inventory_slots` hint；我们应用好 schema，而非 reinvent。
4. **PoE2DB modifier 完整度** — 数据 reference 已饱和；价值在 **build 语境下的 transformed guidance**。
5. **Reddit build 索引** — 聚合功能有；缺的是 **structured vetting**，不是另一个链接列表。
6. **Beginner checklist** — 你们站点已有（`beginner-build-checklist.html`）；可升级为 per-build defense diagnostic，而非从零发明。

---

## 产品定位一句话

> **不是 PoE2 版 op.gg，而是把「选 build → 验属性 → 配 gear → 搜 trade → 导入游戏」串成一条决策链的 Build Decision Assistant**——竞品各管一段，research 证明玩家 pain 恰在段与段之间的断裂处（`README.md` expert model + `01-site-capability-gap.md` 六大 JTBD）。

## Sources

- Research cards `01`–`12` in this folder
- Site under review: https://brickerp.github.io/poe2-build-lab/
- Official Build Planner docs: https://www.pathofexile.com/developer/docs/game
- GGG skill tree export: https://github.com/grindinggear/poe2-skilltree-export
- PoE2DB modifiers: https://poe2db.tw/us/Modifiers
- Reddit build index/trust warning: https://www.reddit.com/r/pathofexile2builds/comments/1tny1to/05_return_of_the_ancients_league_starter_build/
- Reddit build planner demand: https://www.reddit.com/r/pathofexile2builds/comments/1tsen1b/popular_guides_with_the_new_in_game_build_planner/
