# Zotero 9 for Windows 使用指南

> 适用版本：Zotero 9.0.x（2026-04-10 发布）
> 当前稳定版：9.0.5（2026-07）
> 作者：optics-lead（基于网络资料整理）
> 最后更新：2026-07-20

---

## 目录

1. [Zotero 9 新特性概览](#1-zotero-9-新特性概览)
2. [安装与初始设置](#2-安装与初始设置)
3. [必装插件清单](#3-必装插件清单)
4. [中英文划词翻译方案](#4-中英文划词翻译方案)
5. [AI / LLM 集成方案](#5-ai--llm-集成方案)
6. [Agent（MCP）接入——Claude Code 直连 Zotero 文献库](#6-agentmcp-接入claude-code-直连-zotero-文献库)
7. [坚果云同步配置](#7-坚果云同步配置)
8. [常用工作流](#8-常用工作流)
9. [插件速查表](#9-插件速查表)
10. [常见问题与排错](#10-常见问题与排错)

---

## 1. Zotero 9 新特性概览

Zotero 自 2026 年起采用快速发布周期（约每 6–10 周一个大版本）：

| 版本 | 发布日期 | 主要变化 |
|------|---------|---------|
| Zotero 8 | 2026-01-22 | 重新设计的引用对话框、阅读器主题、笔记标签页、注释列表显示 |
| **Zotero 9** | **2026-04-10** | **朗读功能、最近阅读、直接插入注释到文字处理器、改进协作** |

### Zotero 9 重点新功能

1. **Read Aloud（朗读）**：内置屏幕朗读器，可用自然语音朗读 PDF、EPUB 和网页，支持保存阅读位置和自动标注段落。最高支持 3× 倍速。
2. **Recently Read（最近阅读）**：自动跟踪阅读进度，生成「最近阅读」集合。
3. **Add Annotation（插入注释）**：Word/LibreOffice 插件新增按钮，可直接将 Zotero 中的注释（含图片和墨迹注释）作为活动引文插入文档，自动生成参考文献条目。
4. **改进了协作功能**：可以识别谁在群组文献库中添加或修改了参考文献。
5. **更快的性能**：特别是大型文献库的搜索和索引。
6. **浏览器登录**：支持密码管理器和二因素认证，不再需要传统 API key 设置流程。
7. **修复**：Word 集成在 Windows 安全更新后的兼容性问题（KB5094126）。

---

## 2. 安装与初始设置

### 2.1 下载安装

1. **官网下载**：<https://www.zotero.org/download/>
   - 选择 **Zotero 9 for Windows**（64 位）
   - 另有 **Windows ARM** 版本（Surface Pro X 等设备）
2. 运行安装程序，按向导完成安装。
3. **安装浏览器 Connector**：
   - 在下载页同时安装 **Zotero Connector** 浏览器扩展
   - 支持 Chrome、Firefox、Edge、Safari
   - 功能：一键从学术网站（arXiv、Google Scholar、PubMed、知网等）抓取文献题录和 PDF

### 2.2 首次启动设置

```
编辑 → 设置（或 Ctrl+,）
```

重点检查以下几个标签页：

**通用（General）**：
- 「Open the Reader automatically when an item is selected」——建议开启
- 「Automatically annotate passages when using Read Aloud」——朗读时自动标注

**同步（Sync）**：
- 注册或登录 Zotero 账户（免费 300MB 存储，用于同步条目元数据和笔记）
- 文件同步见下文「坚果云同步配置」

**搜索（Search）**：
- 建议勾选「Full-text indexing」自动索引 PDF 全文

### 2.3 Word 插件

安装 Zotero 时会自动安装 Word 加载项。验证方式：
- 打开 Word → 菜单栏应有 **Zotero** 标签
- 如果没出现：Zotero 中 `编辑 → 设置 → 引用 → 重新安装 Word 加载项`

**Zotero 9 新增**：Word 插件中有一个 **Add Annotation** 按钮，可以直接把 Zotero 中的注释以引文形式插入文档。

---

## 3. 必装插件清单

Zotero 插件以 `.xpi` 文件安装。安装方式：

```
工具 → 附加组件（Add-ons）→ 齿轮图标 → Install Add-on From File... → 选择 .xpi
```

### 核心推荐（按优先级）

| 插件 | 星标 | 用途 | 安装建议 |
|------|------|------|---------|
| **Better BibTeX for Zotero** | ~6.9k | LaTeX/BibTeX 导出、稳定引用键 | **必装**（如果写 LaTeX/Overleaf/Markdown） |
| **Translate for Zotero** | ~11.3k | 划词翻译，支持 20+ 翻译服务 | **必装**（英文文献阅读核心） |
| **Jasminum（茉莉花）** | ~7k | 知网 CNKI 元数据抓取、中文作者名切分 | **中文文献必装** |
| **Better Notes for Zotero** | ~8k | 双向链接 Markdown 笔记、模板 | **强烈推荐** |
| **Actions & Tags for Zotero** | ~2.7k | 自动标签、批量操作、工作流自动化 | **强烈推荐** |
| **ZotMoov** | ~1.4k | 附件自动重命名和管理 | 推荐（ZotFile 后继者） |
| **Linter for Zotero** | ~1k | 元数据格式化（HTML 样式、大小写标准化） | 推荐 |
| **Ethereal Style** | ~5k | 文献库界面美化、可视化 | 可选 |
| **Zotero OCR** | ~800 | 扫描版 PDF 的 OCR 文字识别 | 扫描文献必备 |
| **Green Frog** | ~900 | 查看/更新期刊影响因子、中科院/JCR 分区 | 科研评价必备 |

### 安装技巧

- 优先使用 **Add-on Market for Zotero**（~1.6k 星标）插件：安装后在 Zotero 内直接浏览和安装插件，无需手动下载 `.xpi`
- 插件商店（中文社区镜像）：<https://zotero-chinese.com/plugins/>

---

## 4. 中英文划词翻译方案

### 方案一：Translate for Zotero（推荐首选）

**功能**：划词翻译、批注翻译、标题/摘要翻译。支持 20+ 翻译引擎。

**安装**：在 Zotero 插件商店搜索 "Translate for Zotero"

**配置**：
```
编辑 → 设置 → Translate for Zotero
```
- 翻译引擎：推荐 **DeepL**（学术翻译质量最好，需申请免费 API key）或 **谷歌翻译**（免费无 key）
- 备选：**有道翻译**、**百度翻译**、**微软翻译**等
- 建议关闭「自动添加到笔记」（避免笔记被机器翻译内容污染）
- 调整字号为 14–16

**使用**：
- 选中 PDF 中的文字 → 右键 → Translate
- 或选中文字后按快捷键（默认 Ctrl+Shift+T）
- 结果在右侧面板显示

### 方案二：Zotero Pdf2zh（PDF 全文翻译）

**功能**：将整个 PDF 翻译为双语对照版本（原文 + 译文并列），保留排版。

**安装**：Zotero 插件商店搜索 "Zotero Pdf2zh"

**使用**：
- 在 Zotero 中选中文献 → 右键 → Pdf2zh → 翻译
- 生成新的双语 PDF，保留原图

### 方案三：沉浸式翻译（Immersive Translate）

**功能**：Zotero BabelDOC 插件，保留排版的 PDF 全文翻译。

**注意**：需沉浸式翻译 Pro 会员。

### 方案四：HJFY Split Reader（分屏翻译）

**功能**：获取 arXiv 论文的幻觉翻译译文，原文和译文分屏并排打开。

**适用**：arXiv 论文阅读，Zotero 8/9 专用。

### 划词翻译总结

| 需求 | 推荐方案 |
|------|---------|
| 日常划词翻译（偶尔查单词/段落） | **Translate for Zotero**（DeepL 引擎） |
| 整篇 PDF 直译对照阅读 | **Zotero Pdf2zh** 或 **沉浸式翻译** |
| arXiv 论文快速双语阅读 | **HJFY Split Reader** |

---

## 5. AI / LLM 集成方案

Zotero 9 的 AI 生态非常丰富，以下按用途分类：

### 5.1 在 Zotero 内直接与论文对话

| 插件 | 星标 | 特点 |
|------|------|------|
| **PapersGPT** | ~2.5k | 支持 ChatGPT、Gemini、Claude、DeepSeek、GLM 等多模型；在 Zotero 内对话 PDF |
| **Awesome GPT** | ~7.2k | GPT Meet Zotero，通用 AI 对话 |
| **AI4Paper** | ~2.5k | 内置知识库 + 2.4 亿文献源 + PDF 全文翻译 |
| **Beaver** | ~213 | AI 研究助手，对话式探索文献库 |
| **AI Paper Chat** | ~26 | 轻量级 Zotero AI 对话 |
| **MarginMind** | ~2 | 选中文字即可解释/批判/翻译/总结 |

### 5.2 自动精读与笔记生成

| 插件 | 星标 | 特点 |
|------|------|------|
| **zotero-ai-butler（AI 管家）** | ~1.5k | 自动精读论文库中的 PDF，生成结构化 Zotero 笔记 |
| **llm-for-zotero** | ~2.3k | 开源研究 agent，深度融入 Zotero 文献库 |
| **Better Notes** | ~8k | 搭配 AI 使用效果更佳（含 ChatGPT 可扩展性） |

### 5.3 配置建议

如果写 `papers/mie-f/` 下的复现需要大量阅读英文文献，推荐组合：

```
Translate for Zotero（翻译）
+ PapersGPT 或 Awesome GPT（AI 对话）
+ Better Notes（笔记管理）
```

---

## 6. Agent（MCP）接入——Claude Code 直连 Zotero 文献库

**这是你最可能感兴趣的部分**——通过 MCP 协议让 Claude Code（及其他 AI agent）直接读写你的 Zotero 文献库。

### 6.1 Zotero-MCP-Neo（推荐，功能最全）

GitHub: <https://github.com/X-T-E-R/Zotero-MCP-Neo>

一个 Zotero 插件，在 Zotero **内部**嵌入 MCP 服务器，让 AI 助手通过 6 个统一工具完整访问文献库。

#### 安装

1. 从 [Releases](https://github.com/X-T-E-R/Zotero-MCP-Neo/releases) 下载 `.xpi` 文件
2. Zotero → `工具 → 附加组件 → 齿轮图标 → Install Add-on From File...` → 选择 `.xpi`
3. 重启 Zotero

#### 启用服务器

```
编辑 → 设置 → Zotero MCP Neo
```
- 勾选 **Enable Server**
- 端口：默认 `23120`
- 可在设置中配置写权限层级（readonly / create / full / custom）

#### 配置 Claude Code

```bash
claude mcp add --transport http zotero-mcp-neo http://127.0.0.1:23120/mcp
```

或直接编辑 Claude Code 的 MCP 配置（`~/.claude/settings.json`）：

```json
{
  "mcpServers": {
    "zotero-mcp-neo": {
      "transport": "streamable_http",
      "url": "http://127.0.0.1:23120/mcp"
    }
  }
}
```

#### 6 个统一工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `zotero_status` | 检查连接和权限 | `{}` |
| `zotero_list` | 浏览集合、文献、注释 | `{scope: "collection:ABC123"}` |
| `zotero_find` | 按关键词搜索（含语义搜索） | `{query: "Mie scattering", type: "fulltext"}` |
| `zotero_read` | 深入读取单条文献（带分页内容） | `{key: "XYZ789", sections: ["content"], page: 1}` |
| `zotero_write` | 创建/更新/删除（默认 dryRun） | `{action: "create_item", params: {...}, dryRun: true}` |
| `zotero_task` | [实验性] 异步 AI 任务 | 预留 |

#### 使用场景示例

```
Claude：帮我在 Zotero 里找关于 "Mie scattering" 的文献全文
→ Zotero-MCP-Neo 搜索文献库 → 返回匹配结果
```

```
Claude：在 Zotero 中为这篇 PDF 创建条目，DOI 是 10.1364/...
→ Zotero-MCP-Neo 自动获取元数据并创建条目
```

还支持语义搜索（配置 OpenAI/Ollama/Gemini/智谱等嵌入模型），以及导出 SKILL.md 给 AI 客户端。

### 6.2 ZotSeek（轻量替代，语义搜索 + MCP）

GitHub: <https://github.com/introfini/ZotSeek>

- **内置 MCP 服务器**，Claude Code、Codex 可直接连接
- 100% 本地运行，注重隐私
- 语义搜索基于 Transformers.js，纯 CPU 运行
- 当前主要优化英文

配置 Claude Code：
```bash
claude mcp add --transport http zotseek http://127.0.0.1:23121/mcp
```

### 6.3 Zotero Assistant（在 Zotero 内直接调用 LLM）

GitHub: <https://github.com/origin652/zotero-assistant>

- 在 Zotero 9 界面中增加 AI 助手面板
- 可配置任意兼容的 API（OpenAI、Anthropic、Ollama、DeepSeek 等）
- 支持：组织文献、阅读当前 PDF/EPUB、创建笔记、更新元数据、管理标签和集合
- 三种安全模式：AI review（默认）、Confirm（需确认）、Open（无确认）
- 支持中文/英文界面

### 6.4 MCP 接入方案对比

| 方案 | 类型 | 需要额外服务 | 读写 | 适合 |
|------|------|-------------|------|------|
| **Zotero-MCP-Neo** | Zotero 插件 | 无 | 读写（dryRun 安全） | **Claude Code 主力推荐** |
| **ZotSeek** | Zotero 插件 | 无 | 只读为主 | 轻量语义搜索 |
| **cookjohn/zotero-mcp** | Zotero 插件 | 无 | 读写（20+ 工具） | 功能全面的原版 |
| **Zotero Assistant** | Zotero 插件 | LLM API key | 读写（三种安全模式） | 在 Zotero 界面内用 AI |
| **llm-for-zotero** | Zotero 插件 | LLM API key | 读写 | 研究 agent 系统 |
| **richardjlyon/zotero-mcp** | 独立进程 | Python + Zotero | 读写 + OAuth | Claude.ai 网页版接入 |

### 6.5 对 mie-f 复现工作流的实际用途

你写 `papers/mie-f/` 的两篇论文复现时，Zotero + MCP 可以帮你：

1. **文献检索**：Claude 直接在你的 Zotero 文献库中搜索相关论文
2. **元数据自动提取**：输入 DOI，自动创建带完整元数据的条目
3. **PDF 全文读取**：Claude 直接读 Zotero 中已附加的 PDF 全文
4. **注释读取**：读取你在 PDF 上的高亮和批注
5. **引文导出**：直接获取引用信息，用于 LaTeX/Markdown 写作

---

## 7. 坚果云同步配置

Zotero 官方存储只有 300MB，装几个 PDF 就满了。推荐用**坚果云**（每月 1GB 上传、3GB 下载，够用）。

### 方案一：坚果云官方同步插件（推荐，最新方案）

需要坚果云客户端 7.2.8+：

1. 打开坚果云客户端 → 左侧「应用推荐」
2. 找到「Zotero 同步插件」→ 点击「下载安装」
3. 坚果云自动拉起 Zotero 安装插件
4. Zotero 中：`编辑 → 设置 → 同步 → 文件同步`
   - 确保勾选「同步附件到我的文库」
   - 方式选择 **WebDAV**（插件会截胡接管底层传输）
5. 回到坚果云 → 应用推荐 → Zotero 同步插件 → 点击「验证坚果云服务」
6. 提示「验证成功」即可

**优点**：增量同步、无 API 频率限制、大文件不限速。

### 方案二：传统 WebDAV 配置

如果不用坚果云客户端插件，手动配置：

1. 坚果云网页端 → 右上角用户名 → **账户信息 → 安全 → 第三方应用管理 → 添加应用密码**
2. Zotero 中：`编辑 → 设置 → 同步 → 文件同步`
   - 将「我的文库附件同步方式」改为 **WebDAV**
   - URL：`https://dav.jianguoyun.com/dav`
   - 用户名：坚果云账号
   - 密码：刚才生成的应用密码（**不是**登录密码）
   - 点击 **Verify Server** 验证
3. 同步按钮开始同步

> ⚠️ 传统 WebDAV 有半小时内请求次数限制（约几百次），大量批量添加文献时可能报错。建议用方案一。

---

## 8. 常用工作流

### 8.1 文献收集

```
浏览器看论文
  → 点 Zotero Connector 图标
  → 自动抓取题录 + PDF（如果有权限）
  → 自动进入 Zotero 对应集合
```

- **英文**：arXiv、PubMed、Google Scholar、IEEE、OSA/OPTICA 等完美支持
- **中文**：需要安装 Jasminum（茉莉花）插件 + translators_CN 浏览器扩展

### 8.2 文献阅读与批注

```
在 Zotero 中双击文献 → 打开内置 PDF 阅读器
  → 高亮、标注、划线（颜色编码）
  → 选中文字调出 Translate for Zotero 划词翻译
  → 侧边栏写笔记（Better Notes 增强）
  → 朗读（Read Aloud 听论文）
```

**标注颜色推荐约定**：
- 黄色：核心论点
- 绿色：方法/实验
- 蓝色：数据/结果
- 红色：疑问/需要验证

### 8.3 在写作中引用

```
在 Word/Overleaf 中
  → 点 Zotero 插件按钮 → 搜索文献 → 插入引文
  → 自动生成参考文献列表（支持 10000+ 引文格式）
```

- **Word**：使用 Zotero 自带的 Word 插件
- **LaTeX/Overleaf**：使用 Better BibTeX 导出 `.bib` 文件，自动同步
- **Markdown**：用 Better BibTeX 导出 BibTeX，配合 Pandoc citeproc

### 8.4 结合 Agent 自动处理文献

```
Zotero 中收集文献
  → 启动 Claude Code，通过 Zotero-MCP-Neo 连接文献库
  → Claude 自动读取新文献的 PDF 全文
  → 生成摘要、提取参数表
  → 与 mie-f 复现工作流直接对接
```

---

## 9. 插件速查表

### 分类速查

| 类别 | 插件名 | 星标 | 一句话 |
|------|--------|------|--------|
| **翻译** | Translate for Zotero | ★11.3k | 划词翻译，20+ 引擎 |
| | Zotero Pdf2zh | ★5.1k | PDF 全文翻译为双语 |
| | 沉浸式翻译 BabelDOC | ★329 | Pro 会员全文翻译 |
| **笔记** | Better Notes | ★8.0k | Markdown 双链笔记 |
| | Ze Notes | ★104 | 笔记可视化 |
| **AI** | Awesome GPT | ★7.2k | GPT 接入 Zotero |
| | PapersGPT | ★2.5k | 多模型 AI 论文对话 |
| | AI4Paper | ★2.5k | 知识库+翻译+综述 |
| | llm-for-zotero | ★2.3k | 开源研究 agent |
| | zotero-ai-butler | ★1.5k | 自动精读论文 |
| | Beaver | ★213 | AI 研究助手 |
| | AI Paper Chat | ★26 | 轻量 Zotero AI |
| **Agent/MCP** | Zotero MCP Plugin | ★1k | Zotero 嵌入式 MCP 服务器 |
| | ZotSeek | ★159 | 语义搜索 + MCP |
| | Zotero Assistant | new | 桌面 AI 助手插件 |
| **中文** | Jasminum（茉莉花） | ★7k | 知网元数据 |
| **引用/BibTeX** | Better BibTeX | ★6.9k | LaTeX/BibTeX 必备 |
| | Easier Citation | ★1.2k | Word 引用增强 |
| **界面** | Ethereal Style | ★5.1k | 界面美化 |
| | Zutilo | ★1.8k | 编辑增强 |
| | Add-on Market | ★1.6k | 插件内浏览安装 |
| **元数据** | Linter for Zotero | ★1k | 元数据格式化 |
| | Green Frog | ★900 | 影响因子 |
| | Zotero IF | ★467 | 影响因子更新 |
| **自动化** | Actions & Tags | ★2.7k | 自动标记/工作流 |
| **附件** | ZotMoov | ★1.4k | 附件管理（ZotFile 后继） |
| | Zotero Attanger | ★1.3k | 附件管理器 |
| | Sci-PDF | ★969 | Sci-Hub 下 PDF |
| **同步** | Nutstore SSO | ★56 | 坚果云官方同步插件 |
| | 蒲公英 | ★462 | 设置备份/恢复 |
| **查重** | Zoplicate | ★930 | 查重去重 |
| **OCR** | Zotero OCR | ★804 | 扫描件文字识别 |

### 我的推荐组合

根据你的用途（mie-f 论文复现 + 英文文献阅读为主）：

```
基础层：
  Translate for Zotero    ← 划词翻译
  Jasminum                ← 中文文献（知网）
  Better BibTeX           ← LaTeX/Overleaf 导出
  Better Notes            ← 笔记管理

AI 层（三选一，别全装）：
  PapersGPT               ← 论文对话 + 多模型支持
  或 Awesome GPT          ← 通用 AI 对话
  或 zotero-ai-butler     ← 自动精读

Agent 层（必装，Claude Code 对接）：
  Zotero-MCP-Neo          ← Claude Code 直接搜读写文献库

同步层：
  坚果云官方同步插件       ← 多端同步

可选增强：
  Actions & Tags          ← 自动分类、标记
  Green Frog              ← 看影响因子/分区
  Linter for Zotero       ← 元数据清洗
```

---

## 10. 常见问题与排错

### 10.1 Word 插件不工作

Zotero 9.0.5 已修复 Windows 上 Word 的集成问题（KB5094126 安全更新导致）。如果仍有问题：

1. `编辑 → 设置 → 引用 → 重新安装 Word 加载项`
2. 检查 Word 中是否禁用了 Zotero 加载项（Word → 文件 → 选项 → 加载项）
3. 以管理员身份运行一次 Zotero

### 10.2 同步冲突/频繁报错

- 传统 WebDAV 遇请求频繁 → 切为**坚果云官方同步插件**
- 同一条目被多设备修改 → Zotero 会保留版本历史，手动选择保留哪个

### 10.3 搜索不更新

Zotero 9.0.4 修复了「长时间打开后搜索/索引失效」的 bug。升级到最新版即可。

### 10.4 插件安装失败

- 确认下载的 `.xpi` 与 Zotero 版本兼容（Zotero 9 插件通常标为 `Zotero 7+` 或 `Zotero 8-9`）
- 如果从 GitHub 下载，确保下载的是完整的 `.xpi` 文件而非源码
- 尝试重启 Zotero 后再安装

### 10.5 MCP 连接不上

- 确认 Zotero 正在运行（MCP 服务器嵌入在 Zotero 进程中）
- 确认插件设置中 **Enable Server** 已勾选
- 检查端口是否被占用（默认 23120）
- 防火墙是否拦截了本地回环连接
- Claude Code 中运行 `claude mcp list` 查看 MCP 连接状态

### 10.6 批量导入已有 PDF

1. 把 PDF 拖入 Zotero 窗口
2. 或：文件 → 导入 → 文件夹导入（配合 Folder Import 插件更高效）
3. Zotero 会自动尝试检索元数据（通过 DOI、ISBN 等）
4. 检索不到的：右键 → 重新抓取元数据，或手动填写

### 10.7 数据备份

Zotero 数据目录默认在：
```
C:\Users\<用户名>\Zotero
```

建议定期备份整个目录，或使用 **蒲公英** 插件备份设置。

---

## 附录：推荐资源

- **Zotero 中文社区**：<https://zotero-chinese.com/>（插件商店、使用手册、CSL 样式）
- **Zotero 官方插件列表**：<https://www.zotero.org/support/plugins>
- **Zotero MCP Neo**：<https://github.com/X-T-E-R/Zotero-MCP-Neo>
- **ZotSeek**：<https://github.com/introfini/ZotSeek>
- **Zotero 中文插件商店**：<https://zotero-chinese.com/plugins/>
- **Better BibTeX 文档**：<https://retorquere.github.io/zotero-better-bibtex/>

---

*本指南基于 2026-07-20 公开信息整理。Zotero 版本快速迭代中，建议定期关注更新。*
