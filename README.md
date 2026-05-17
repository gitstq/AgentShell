<p align="center">
  <a href="#简体中文">简体中文</a> &nbsp;|&nbsp;
  <a href="#繁體中文">繁體中文</a> &nbsp;|&nbsp;
  <a href="#english">English</a>
</p>

---

<a id="简体中文"></a>

# AgentShell

<p align="center">
  <strong>轻量级终端命令 Agent 化包装引擎</strong><br/>
  <em>Lightweight Terminal Command Agent-Native Wrapping Engine</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="python"/>
  <img src="https://img.shields.io/badge/dependencies-zero-orange" alt="dependencies"/>
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license"/>
</p>

---

## 🎉 项目介绍

**AgentShell** 是一款面向 AI Agent 时代的终端命令包装引擎。它能自动解析任意 CLI 工具的帮助信息，将其转化为 AI Agent 可直接理解的结构化工具描述（兼容 MCP / OpenAI Function Calling 格式），并提供安全沙箱执行、命令模板系统、MCP Server 模式等能力，让 AI Agent 真正"学会"使用终端命令。

> 💡 **核心理念**：不造轮子，只做桥梁 —— 把终端里已有的海量 CLI 工具，以 Agent 友好的方式暴露给 AI。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **CLI 工具分析器** | 自动解析命令帮助信息，生成 AI Agent 可理解的工具 Schema（兼容 MCP / OpenAI Function Calling 格式） |
| 🛡️ **安全沙箱执行引擎** | 内置危险命令拦截、磁盘写检测、网络访问检测、超时控制，让 Agent 放心执行命令 |
| 📋 **命令模板系统** | 内置 11 个常用工具模板（git / docker / npm / pip / python / curl / jq / grep / find / tar / ssh），开箱即用 |
| 🌐 **MCP Server 模式** | 通过 HTTP 端点将工具暴露给 AI Agent（Claude / Cursor 等），即开即连 |
| 📊 **执行历史记录** | 自动记录每次执行，支持搜索、统计、JSON / 文本导出 |
| 🪶 **零外部依赖** | 纯 Python 标准库实现，Python 3.8+ 即可运行，安装即用 |

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.8
- **操作系统**：Linux / macOS / Windows
- **外部依赖**：无（零依赖设计）

### 安装

**方式一：从 GitHub 直接安装**

```bash
pip install git+https://github.com/gitstq/AgentShell.git
```

**方式二：克隆后本地安装（推荐开发时使用）**

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .
```

### 验证安装

```bash
agentshell --version
# AgentShell v1.0.0
```

### 三步上手

```bash
# 1️⃣ 分析一个 CLI 工具，生成 Agent 可理解的 Schema
agentshell analyze git

# 2️⃣ 在安全沙箱中执行命令
agentshell run ls -la

# 3️⃣ 启动 MCP Server，让 AI Agent 调用你的终端工具
agentshell serve --port 8765
```

---

## 📖 详细使用指南

### `analyze` — 分析 CLI 工具

自动解析命令的帮助信息，提取子命令、参数、选项等结构化数据。

```bash
# 分析 git 命令
agentshell analyze git

# 分析 docker 命令，并以 JSON 格式输出
agentshell analyze docker --json

# 自定义帮助命令超时时间（默认 10 秒）
agentshell analyze kubectl --timeout 15
```

### `run` — 安全执行命令

在沙箱中执行命令，自动进行安全检查。

```bash
# 安全执行命令
agentshell run ls -la

# 执行带管道的命令
agentshell run "cat /etc/hosts | grep localhost"

# 自定义超时时间（默认 30 秒）
agentshell run "sleep 5" --timeout 10

# 额外屏蔽特定命令模式
agentshell run "some-command" --block "dangerous-pattern"

# JSON 格式输出（便于程序处理）
agentshell run "echo hello" --json
```

> ⚠️ 沙箱会自动检测并拦截以下危险操作：
> - `rm -rf /` 等破坏性命令
> - `mkfs`、`dd` 等磁盘级操作
> - `shutdown`、`reboot` 等系统控制命令
> - Fork 炸弹等资源耗尽攻击

### `template` — 模板管理

管理内置的命令模板，快速获取常用工具的结构化描述。

```bash
# 列出所有可用模板
agentshell template list

# 查看某个模板的详细信息
agentshell template show git

# 搜索模板
agentshell template search container

# JSON 格式输出
agentshell template list --json
agentshell template show docker --json
```

**内置模板一览：**

| 模板 | 说明 |
|------|------|
| `git` | 分布式版本控制系统 |
| `docker` | 容器化应用管理平台 |
| `npm` | Node.js 包管理器 |
| `pip` | Python 包安装器 |
| `python` | Python 解释器 |
| `curl` | 命令行数据传输工具 |
| `jq` | 命令行 JSON 处理器 |
| `grep` | 文本模式搜索工具 |
| `find` | 文件和目录搜索工具 |
| `tar` | 归档压缩工具 |
| `ssh` | 安全远程登录工具 |

### `serve` — 启动 MCP Server

将内置模板作为工具通过 HTTP 端点暴露给 AI Agent。

```bash
# 使用默认端口 8765 启动
agentshell serve

# 指定端口启动
agentshell serve --port 9000
```

启动后可用的端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/tools` | GET | 列出所有已暴露的工具 |
| `/tools/<name>` | POST | 调用指定工具 |
| `/config` | GET | 获取 MCP 配置信息 |
| `/health` | GET | 健康检查 |

### `schema` — 生成工具 Schema

为指定命令生成兼容 MCP / OpenAI Function Calling 格式的工具 Schema。

```bash
# 生成 curl 的工具 Schema
agentshell schema curl

# 生成 docker 的工具 Schema
agentshell schema docker
```

输出示例（JSON 格式）：

```json
{
  "type": "function",
  "function": {
    "name": "shell_curl",
    "description": "Command-line tool for transferring data with URL syntax...",
    "parameters": {
      "type": "object",
      "properties": {
        "subcommand": {
          "type": "string",
          "description": "The subcommand or action to perform."
        }
      }
    }
  }
}
```

### `history` — 执行历史

查看、搜索和统计命令执行历史。

```bash
# 查看最近 20 条执行记录
agentshell history

# 搜索历史记录
agentshell history "git push"

# 查看执行统计
agentshell history --stats

# 导出为 JSON 格式
agentshell history --export json

# 导出为文本格式
agentshell history --export text

# 清空历史记录
agentshell history --clear
```

### 全局 `--json` 选项

所有子命令都支持 `--json` 标志，输出结构化 JSON 数据，方便程序集成和自动化处理。

```bash
agentshell --json analyze git
agentshell --json run "echo hello"
agentshell --json template list
```

---

## 💡 设计思路与迭代规划

### 设计哲学

1. **零依赖原则** —— 仅使用 Python 标准库，降低安装门槛，避免依赖冲突
2. **渐进式抽象** —— 从简单的命令分析到完整的 MCP Server，按需使用
3. **安全优先** —— 内置多层安全检查，让 AI Agent 执行命令时不必提心吊胆
4. **格式兼容** —— 生成的 Schema 兼容 MCP 和 OpenAI Function Calling，无缝对接主流 Agent 框架

### 迭代规划

- [x] v1.0.0 — 核心功能：CLI 分析器、安全沙箱、模板系统、MCP Server、执行历史
- [ ] v1.1.0 — 自定义模板注册与持久化存储
- [ ] v1.2.0 — 插件系统，支持第三方扩展
- [ ] v2.0.0 — 原生 MCP 协议支持（SSE / stdio transport）

---

## 📦 安装与部署

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell

# 开发模式安装（推荐）
pip install -e .

# 或普通安装
pip install .
```

### 从 PyPI 安装（如已发布）

```bash
pip install agentshell
```

### 在 Docker 中使用

```bash
docker run -it --rm python:3.11-slim bash -c "
  pip install git+https://github.com/gitstq/AgentShell.git &&
  agentshell --version
"
```

### 与 AI Agent 集成

**Claude Desktop 配置示例：**

在 Claude Desktop 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "agentshell": {
      "command": "agentshell",
      "args": ["serve", "--port", "8765"]
    }
  }
}
```

**Cursor / 其他 Agent 配置：**

```bash
# 启动 MCP Server
agentshell serve --port 8765

# Agent 通过 HTTP 调用工具
# GET  http://127.0.0.1:8765/tools        — 发现工具
# POST http://127.0.0.1:8765/tools/shell_git — 调用工具
```

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是提交 Bug、改进文档，还是贡献新功能。

### 参与步骤

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 开发环境搭建

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .

# 运行测试
python -m pytest tests/
```

### 代码规范

- 遵循 PEP 8 编码规范
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
- 新功能请附带对应的单元测试

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 AgentShell Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentShell">AgentShell Team</a>
</p>

---
---

<a id="繁體中文"></a>

# AgentShell

<p align="center">
  <strong>輕量級終端命令 Agent 化包裝引擎</strong><br/>
  <em>Lightweight Terminal Command Agent-Native Wrapping Engine</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="python"/>
  <img src="https://img.shields.io/badge/dependencies-zero-orange" alt="dependencies"/>
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license"/>
</p>

---

## 🎉 專案介紹

**AgentShell** 是一款面向 AI Agent 時代的終端命令包裝引擎。它能自動解析任意 CLI 工具的說明資訊，將其轉化為 AI Agent 可直接理解的結構化工具描述（相容 MCP / OpenAI Function Calling 格式），並提供安全沙箱執行、命令模板系統、MCP Server 模式等能力，讓 AI Agent 真正「學會」使用終端命令。

> 💡 **核心理念**：不造輪子，只做橋樑 —— 把終端裡已有的海量 CLI 工具，以 Agent 友好的方式暴露給 AI。

---

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔍 **CLI 工具分析器** | 自動解析命令說明資訊，生成 AI Agent 可理解的工具 Schema（相容 MCP / OpenAI Function Calling 格式） |
| 🛡️ **安全沙箱執行引擎** | 內建危險命令攔截、磁碟寫入偵測、網路存取偵測、逾時控制，讓 Agent 放心執行命令 |
| 📋 **命令模板系統** | 內建 11 個常用工具模板（git / docker / npm / pip / python / curl / jq / grep / find / tar / ssh），開箱即用 |
| 🌐 **MCP Server 模式** | 透過 HTTP 端點將工具暴露給 AI Agent（Claude / Cursor 等），即開即連 |
| 📊 **執行歷史記錄** | 自動記錄每次執行，支援搜尋、統計、JSON / 文字匯出 |
| 🪶 **零外部依賴** | 純 Python 標準函式庫實作，Python 3.8+ 即可執行，安裝即用 |

---

## 🚀 快速開始

### 環境需求

- **Python** >= 3.8
- **作業系統**：Linux / macOS / Windows
- **外部依賴**：無（零依賴設計）

### 安裝

**方式一：從 GitHub 直接安裝**

```bash
pip install git+https://github.com/gitstq/AgentShell.git
```

**方式二：複製後本機安裝（推薦開發時使用）**

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .
```

### 驗證安裝

```bash
agentshell --version
# AgentShell v1.0.0
```

### 三步上手

```bash
# 1️⃣ 分析一個 CLI 工具，生成 Agent 可理解的 Schema
agentshell analyze git

# 2️⃣ 在安全沙箱中執行命令
agentshell run ls -la

# 3️⃣ 啟動 MCP Server，讓 AI Agent 呼叫你的終端工具
agentshell serve --port 8765
```

---

## 📖 詳細使用指南

### `analyze` — 分析 CLI 工具

自動解析命令的說明資訊，提取子命令、參數、選項等結構化資料。

```bash
# 分析 git 命令
agentshell analyze git

# 分析 docker 命令，並以 JSON 格式輸出
agentshell analyze docker --json

# 自訂說明命令逾時時間（預設 10 秒）
agentshell analyze kubectl --timeout 15
```

### `run` — 安全執行命令

在沙箱中執行命令，自動進行安全檢查。

```bash
# 安全執行命令
agentshell run ls -la

# 執行含管線的命令
agentshell run "cat /etc/hosts | grep localhost"

# 自訂逾時時間（預設 30 秒）
agentshell run "sleep 5" --timeout 10

# 額外封鎖特定命令模式
agentshell run "some-command" --block "dangerous-pattern"

# JSON 格式輸出（便於程式處理）
agentshell run "echo hello" --json
```

> ⚠️ 沙箱會自動偵測並攔截以下危險操作：
> - `rm -rf /` 等破壞性命令
> - `mkfs`、`dd` 等磁碟級操作
> - `shutdown`、`reboot` 等系統控制命令
> - Fork 炸彈等資源耗盡攻擊

### `template` — 模板管理

管理內建的命令模板，快速取得常用工具的結構化描述。

```bash
# 列出所有可用模板
agentshell template list

# 查看某個模板的詳細資訊
agentshell template show git

# 搜尋模板
agentshell template search container

# JSON 格式輸出
agentshell template list --json
agentshell template show docker --json
```

**內建模板一覽：**

| 模板 | 說明 |
|------|------|
| `git` | 分散式版本控制系統 |
| `docker` | 容器化應用管理平台 |
| `npm` | Node.js 套件管理器 |
| `pip` | Python 套件安裝器 |
| `python` | Python 直譯器 |
| `curl` | 命令列資料傳輸工具 |
| `jq` | 命令列 JSON 處理器 |
| `grep` | 文字模式搜尋工具 |
| `find` | 檔案與目錄搜尋工具 |
| `tar` | 封存壓縮工具 |
| `ssh` | 安全遠端登入工具 |

### `serve` — 啟動 MCP Server

將內建模板作為工具透過 HTTP 端點暴露給 AI Agent。

```bash
# 使用預設連接埠 8765 啟動
agentshell serve

# 指定連接埠啟動
agentshell serve --port 9000
```

啟動後可用的端點：

| 端點 | 方法 | 說明 |
|------|------|------|
| `/tools` | GET | 列出所有已暴露的工具 |
| `/tools/<name>` | POST | 呼叫指定工具 |
| `/config` | GET | 取得 MCP 設定資訊 |
| `/health` | GET | 健康檢查 |

### `schema` — 生成工具 Schema

為指定命令生成相容 MCP / OpenAI Function Calling 格式的工具 Schema。

```bash
# 生成 curl 的工具 Schema
agentshell schema curl

# 生成 docker 的工具 Schema
agentshell schema docker
```

輸出範例（JSON 格式）：

```json
{
  "type": "function",
  "function": {
    "name": "shell_curl",
    "description": "Command-line tool for transferring data with URL syntax...",
    "parameters": {
      "type": "object",
      "properties": {
        "subcommand": {
          "type": "string",
          "description": "The subcommand or action to perform."
        }
      }
    }
  }
}
```

### `history` — 執行歷史

查看、搜尋和統計命令執行歷史。

```bash
# 查看最近 20 筆執行記錄
agentshell history

# 搜尋歷史記錄
agentshell history "git push"

# 查看執行統計
agentshell history --stats

# 匯出為 JSON 格式
agentshell history --export json

# 匯出為文字格式
agentshell history --export text

# 清空歷史記錄
agentshell history --clear
```

### 全域 `--json` 選項

所有子命令都支援 `--json` 標誌，輸出結構化 JSON 資料，方便程式整合與自動化處理。

```bash
agentshell --json analyze git
agentshell --json run "echo hello"
agentshell --json template list
```

---

## 💡 設計思路與迭代規劃

### 設計哲學

1. **零依賴原則** —— 僅使用 Python 標準函式庫，降低安裝門檻，避免依賴衝突
2. **漸進式抽象** —— 從簡單的命令分析到完整的 MCP Server，按需使用
3. **安全優先** —— 內建多層安全檢查，讓 AI Agent 執行命令時不必提心吊膽
4. **格式相容** —— 生成的 Schema 相容 MCP 和 OpenAI Function Calling，無縫對接主流 Agent 框架

### 迭代規劃

- [x] v1.0.0 — 核心功能：CLI 分析器、安全沙箱、模板系統、MCP Server、執行歷史
- [ ] v1.1.0 — 自訂模板註冊與持久化儲存
- [ ] v1.2.0 — 外掛系統，支援第三方擴充
- [ ] v2.0.0 — 原生 MCP 協議支援（SSE / stdio transport）

---

## 📦 安裝與部署

### 從原始碼安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell

# 開發模式安裝（推薦）
pip install -e .

# 或一般安裝
pip install .
```

### 從 PyPI 安裝（如已發佈）

```bash
pip install agentshell
```

### 在 Docker 中使用

```bash
docker run -it --rm python:3.11-slim bash -c "
  pip install git+https://github.com/gitstq/AgentShell.git &&
  agentshell --version
"
```

### 與 AI Agent 整合

**Claude Desktop 設定範例：**

在 Claude Desktop 的 MCP 設定檔中新增：

```json
{
  "mcpServers": {
    "agentshell": {
      "command": "agentshell",
      "args": ["serve", "--port", "8765"]
    }
  }
}
```

**Cursor / 其他 Agent 設定：**

```bash
# 啟動 MCP Server
agentshell serve --port 8765

# Agent 透過 HTTP 呼叫工具
# GET  http://127.0.0.1:8765/tools        — 發現工具
# POST http://127.0.0.1:8765/tools/shell_git — 呼叫工具
```

---

## 🤝 貢獻指南

我們歡迎任何形式的貢獻！無論是提交 Bug、改善文件，還是貢獻新功能。

### 參與步驟

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 開發環境建置

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .

# 執行測試
python -m pytest tests/
```

### 程式碼規範

- 遵循 PEP 8 編碼規範
- 提交訊息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範
- 新功能請附帶對應的單元測試

---

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

```
MIT License

Copyright (c) 2024 AgentShell Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentShell">AgentShell Team</a>
</p>

---
---

<a id="english"></a>

# AgentShell

<p align="center">
  <strong>Lightweight Terminal Command Agent-Native Wrapping Engine</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="python"/>
  <img src="https://img.shields.io/badge/dependencies-zero-orange" alt="dependencies"/>
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license"/>
</p>

---

## 🎉 Introduction

**AgentShell** is a terminal command wrapping engine built for the AI Agent era. It automatically parses the help output of any CLI tool and converts it into structured tool descriptions that AI Agents can directly understand (compatible with MCP / OpenAI Function Calling formats). It also provides a secure sandbox execution environment, a command template system, an MCP Server mode, and more — empowering AI Agents to truly "learn" how to use terminal commands.

> 💡 **Core Philosophy**: Don't reinvent the wheel — build bridges. Expose the vast ecosystem of existing CLI tools to AI in an Agent-friendly way.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **CLI Tool Analyzer** | Automatically parses command help output and generates AI Agent-readable tool Schemas (compatible with MCP / OpenAI Function Calling formats) |
| 🛡️ **Secure Sandbox Engine** | Built-in dangerous command interception, disk write detection, network access detection, and timeout control — execute commands with confidence |
| 📋 **Command Template System** | 11 built-in tool templates (git / docker / npm / pip / python / curl / jq / grep / find / tar / ssh), ready to use out of the box |
| 🌐 **MCP Server Mode** | Expose tools to AI Agents (Claude / Cursor, etc.) via HTTP endpoints — start and connect instantly |
| 📊 **Execution History** | Automatically records every execution with search, statistics, and JSON / text export support |
| 🪶 **Zero External Dependencies** | Built entirely with the Python standard library — runs on Python 3.8+, install and go |

---

## 🚀 Quick Start

### Prerequisites

- **Python** >= 3.8
- **OS**: Linux / macOS / Windows
- **External Dependencies**: None (zero-dependency design)

### Installation

**Option 1: Install directly from GitHub**

```bash
pip install git+https://github.com/gitstq/AgentShell.git
```

**Option 2: Clone and install locally (recommended for development)**

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .
```

### Verify Installation

```bash
agentshell --version
# AgentShell v1.0.0
```

### Three Steps to Get Started

```bash
# 1️⃣ Analyze a CLI tool and generate an Agent-readable Schema
agentshell analyze git

# 2️⃣ Execute a command in the secure sandbox
agentshell run ls -la

# 3️⃣ Start the MCP Server and let AI Agents call your terminal tools
agentshell serve --port 8765
```

---

## 📖 Detailed Usage Guide

### `analyze` — Analyze CLI Tools

Automatically parses a command's help output and extracts structured data including subcommands, arguments, and options.

```bash
# Analyze the git command
agentshell analyze git

# Analyze the docker command with JSON output
agentshell analyze docker --json

# Customize the help command timeout (default: 10 seconds)
agentshell analyze kubectl --timeout 15
```

### `run` — Execute Commands Safely

Execute commands inside a sandbox with automatic safety checks.

```bash
# Execute a command safely
agentshell run ls -la

# Execute a piped command
agentshell run "cat /etc/hosts | grep localhost"

# Customize the timeout (default: 30 seconds)
agentshell run "sleep 5" --timeout 10

# Block additional command patterns
agentshell run "some-command" --block "dangerous-pattern"

# JSON output (for programmatic processing)
agentshell run "echo hello" --json
```

> ⚠️ The sandbox automatically detects and blocks the following dangerous operations:
> - Destructive commands like `rm -rf /`
> - Disk-level operations like `mkfs`, `dd`
> - System control commands like `shutdown`, `reboot`
> - Resource exhaustion attacks like fork bombs

### `template` — Template Management

Manage built-in command templates and quickly retrieve structured descriptions for common tools.

```bash
# List all available templates
agentshell template list

# View detailed information for a specific template
agentshell template show git

# Search templates
agentshell template search container

# JSON output
agentshell template list --json
agentshell template show docker --json
```

**Built-in Templates:**

| Template | Description |
|----------|-------------|
| `git` | Distributed version control system |
| `docker` | Containerized application management platform |
| `npm` | Node.js package manager |
| `pip` | Python package installer |
| `python` | Python interpreter |
| `curl` | Command-line data transfer tool |
| `jq` | Command-line JSON processor |
| `grep` | Text pattern search tool |
| `find` | File and directory search tool |
| `tar` | Archiving and compression utility |
| `ssh` | Secure remote login tool |

### `serve` — Start MCP Server

Expose built-in templates as tools via HTTP endpoints for AI Agents to consume.

```bash
# Start with the default port 8765
agentshell serve

# Start with a custom port
agentshell serve --port 9000
```

Available endpoints after startup:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools` | GET | List all exposed tools |
| `/tools/<name>` | POST | Invoke a specific tool |
| `/config` | GET | Get MCP configuration |
| `/health` | GET | Health check |

### `schema` — Generate Tool Schema

Generate tool Schemas compatible with MCP / OpenAI Function Calling formats for a given command.

```bash
# Generate a tool Schema for curl
agentshell schema curl

# Generate a tool Schema for docker
agentshell schema docker
```

Example output (JSON format):

```json
{
  "type": "function",
  "function": {
    "name": "shell_curl",
    "description": "Command-line tool for transferring data with URL syntax...",
    "parameters": {
      "type": "object",
      "properties": {
        "subcommand": {
          "type": "string",
          "description": "The subcommand or action to perform."
        }
      }
    }
  }
}
```

### `history` — Execution History

View, search, and analyze command execution history.

```bash
# View the 20 most recent execution records
agentshell history

# Search history records
agentshell history "git push"

# View execution statistics
agentshell history --stats

# Export as JSON
agentshell history --export json

# Export as text
agentshell history --export text

# Clear all history
agentshell history --clear
```

### Global `--json` Flag

All subcommands support the `--json` flag for structured JSON output, making it easy to integrate with scripts and automation pipelines.

```bash
agentshell --json analyze git
agentshell --json run "echo hello"
agentshell --json template list
```

---

## 💡 Design Philosophy & Roadmap

### Design Principles

1. **Zero Dependencies** — Built exclusively with the Python standard library to minimize installation friction and avoid dependency conflicts
2. **Progressive Abstraction** — From simple command analysis to a full MCP Server, use only what you need
3. **Security First** — Multi-layered safety checks so AI Agents can execute commands without worry
4. **Format Compatibility** — Generated Schemas are compatible with both MCP and OpenAI Function Calling, seamlessly integrating with mainstream Agent frameworks

### Roadmap

- [x] v1.0.0 — Core features: CLI analyzer, secure sandbox, template system, MCP Server, execution history
- [ ] v1.1.0 — Custom template registration and persistent storage
- [ ] v1.2.0 — Plugin system with third-party extension support
- [ ] v2.0.0 — Native MCP protocol support (SSE / stdio transport)

---

## 📦 Installation & Deployment

### Install from Source

```bash
# Clone the repository
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell

# Install in development mode (recommended)
pip install -e .

# Or install normally
pip install .
```

### Install from PyPI (when published)

```bash
pip install agentshell
```

### Using with Docker

```bash
docker run -it --rm python:3.11-slim bash -c "
  pip install git+https://github.com/gitstq/AgentShell.git &&
  agentshell --version
"
```

### Integrating with AI Agents

**Claude Desktop configuration example:**

Add the following to Claude Desktop's MCP configuration file:

```json
{
  "mcpServers": {
    "agentshell": {
      "command": "agentshell",
      "args": ["serve", "--port", "8765"]
    }
  }
}
```

**Cursor / Other Agents:**

```bash
# Start the MCP Server
agentshell serve --port 8765

# Agents call tools via HTTP
# GET  http://127.0.0.1:8765/tools          — Discover tools
# POST http://127.0.0.1:8765/tools/shell_git — Invoke a tool
```

---

## 🤝 Contributing

Contributions of all kinds are welcome! Whether it's filing a bug report, improving documentation, or contributing new features.

### How to Contribute

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

### Development Setup

```bash
git clone https://github.com/gitstq/AgentShell.git
cd AgentShell
pip install -e .

# Run tests
python -m pytest tests/
```

### Code Style

- Follow PEP 8 coding conventions
- Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification
- New features should include corresponding unit tests

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 AgentShell Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentShell">AgentShell Team</a>
</p>
