# Linkding Tools

一个功能强大的 Linkding 链接管理工具集，支持从多种数据源导入链接并进行管理。

## 功能

### 配置管理命令（首次使用）

#### `setup-config` - 交互式配置凭证
首次使用前，运行此命令进行安全的交互式配置：

```bash
uv run linkding-tools setup-config
```

该命令会：
1. 提示输入 Linkding 服务地址
2. 提示输入 API Token
3. 验证配置是否有效
4. 将配置保存到 `.env` 文件

#### `test-config` - 验证配置有效性
测试当前配置是否可以连接到 Linkding 服务：

```bash
uv run linkding-tools test-config
```

#### `show-config` - 查看当前配置
显示当前加载的配置（Token 会被屏蔽）：

```bash
uv run linkding-tools show-config
```

### 功能命令

### 1. 上传 Markdown 文件 (`upload-markdown`)
从单个 Markdown 文件中提取链接和标签，然后上传到 Linkding。

**特性：**
- 支持 Markdown 链接格式：`[文本](URL)`
- 支持纯 URL：`https://example.com`
- 自动从列表结构生成多级标签
- 支持自定义基础标签

**示例 Markdown 文件结构：**
```markdown
# 教程

## Python

- [Python 官网](https://www.python.org)
- [Flask 文档](https://flask.palletsprojects.com)

## JavaScript

- [Node.js](https://nodejs.org)
- https://www.npmjs.com
```

**用法：**
```bash
# 基础用法（使用文件名作为基础标签）
python3 linkding-tools.py upload-markdown links.md

# 指定基础标签
python3 linkding-tools.py upload-markdown links.md -t 编程教程

# 跳过确认
python3 linkding-tools.py upload-markdown links.md -y
```

### 2. 上传 JSONL 文件 (`upload-jsonl`)
上传 JSONL 格式（每行一个 JSON 对象）的链接数据。

**JSONL 格式：**
```jsonl
{"url": "https://example.com", "tag_names": ["标签1", "标签2"]}
{"url": "https://example.org", "tag_names": ["标签1", "标签3"]}
```

**用法：**
```bash
python3 linkding-tools.py upload-jsonl bookmarks.jsonl

# 跳过确认
python3 linkding-tools.py upload-jsonl bookmarks.jsonl -y
```

### 3. 导入 Chrome 书签 (`import-chrome`)
导入从 Chrome 导出的书签 HTML 文件，自动保留文件夹结构作为标签。

**用法：**
```bash
# 从 Chrome 导出书签（HTML 格式）后运行
python3 linkding-tools.py import-chrome bookmarks_2026_1_6.html

# 跳过确认
python3 linkding-tools.py import-chrome bookmarks_2026_1_6.html -y
```

### 4. 重命名标签 (`rename-tag`)
批量重命名 Linkding 中的标签。

**用法：**
```bash
# 将标签 "python" 替换为 "Python"
python3 linkding-tools.py rename-tag python Python

# 跳过确认
python3 linkding-tools.py rename-tag python Python -y
```

## 安装

### 使用 uv（推荐）

```bash
# 克隆或进入项目目录
cd /path/to/links

# 使用 uv 安装依赖
uv sync
```

### 使用 pip

```bash
python3 -m pip install -r requirements.txt
```

## 首次配置（必需）

### 方式 1：交互式配置向导（推荐）

```bash
# 首次使用，运行配置向导
uv run linkding-tools setup-config

# 按照提示输入 Linkding 服务地址和 API Token
# 配置会自动保存到 .env 文件
```

### 方式 2：手动配置 .env 文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入实际配置
# LINKDING_URL=https://your-linkding-instance.com
# LINKDING_TOKEN=your_api_token_here
```

### 方式 3：环境变量

```bash
export LINKDING_URL=https://your-linkding-instance.com
export LINKDING_TOKEN=your_api_token_here
uv run linkding-tools
```

### 验证配置

配置完成后，验证是否有效：

```bash
uv run linkding-tools test-config
```

## 配置

### 配置命令（推荐）

使用内置的配置管理命令来管理凭证：

```bash
# 交互式配置（首次使用推荐）
uv run linkding-tools setup-config

# 验证配置是否有效
uv run linkding-tools test-config

# 查看当前配置（Token 被屏蔽）
uv run linkding-tools show-config
```

### 配置加载优先级

工具会按以下优先级加载配置：

1. **环境变量** - `LINKDING_URL` 和 `LINKDING_TOKEN`（最高优先级）
2. **.env 文件** - 项目根目录的 `.env` 文件
3. **交互式提示** - 缺失配置时自动提示输入（最低优先级）

### 方式 1：环境变量（推荐 CI/CD）

```bash
export LINKDING_URL=https://your-linkding-instance.com
export LINKDING_TOKEN=your_api_token_here
uv run linkding-tools upload-markdown links.md
```

### 方式 2：.env 文件（推荐本地开发）

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的配置：
   ```
   LINKDING_URL=https://your-linkding-instance.com
   LINKDING_TOKEN=your_api_token_here
   ```

3. 直接运行工具，会自动读取 `.env` 文件：
   ```bash
   python3 linkding-tools.py upload-markdown links.md
   ```

### 方式 3：交互式输入

不提供环境变量或 .env 文件时，工具会交互式提示输入：
```bash
python3 linkding-tools.py upload-markdown links.md
# 会提示输入 LINKDING_URL 和 LINKDING_TOKEN
```

## 使用模式

### 命令行模式

直接使用子命令执行任务：

```bash
# 查看所有可用命令
python3 linkding-tools.py --help

# 查看特定命令的帮助
python3 linkding-tools.py upload-markdown --help

# 执行命令
python3 linkding-tools.py upload-markdown links.md -t 我的标签
```

### 交互式菜单

不带任何参数运行进入交互式菜单：

```bash
python3 linkding-tools.py
```

菜单会显示所有可用功能，引导你逐步完成操作：

```
==================================================
Linkding Tools - 链接管理工具
==================================================
服务地址: https://your-linkding-instance.com
--------------------------------------------------
1. 上传 Markdown 文件中的链接
2. 上传 JSONL 文件中的链接
3. 导入 Chrome 书签
4. 重命名标签
0. 退出
--------------------------------------------------
请选择功能 [0-4]:
```

## 获取 API Token

1. 登录到你的 Linkding 实例
2. 点击右上角用户头像，选择"Settings"或"设置"
3. 在"API"或"API Token"部分，生成或复制你的 token
4. 保存到 `.env` 文件中

## 快速开始

### 1. 安装和配置

```bash
# 克隆或进入项目目录
cd /path/to/links

# 使用 uv 安装依赖
uv sync

# 交互式配置（推荐）
uv run linkding-tools setup-config

# 验证配置
uv run linkding-tools test-config
```

### 2. 基本使用

```bash
# 交互式菜单（适合新手）
uv run linkding-tools

# 命令行模式（快速执行）
uv run linkding-tools upload-markdown links.md
uv run linkding-tools import-chrome bookmarks.html
uv run linkding-tools rename-tag old-tag new-tag
```

### 3. 常见任务

**导入 Chrome 书签**
```bash
# 1. Chrome → 书签 → 书签管理器 → 导出书签
# 2. 运行导入命令
uv run linkding-tools import-chrome bookmarks.html
```

**上传 Markdown 笔记**
```bash
# 创建 Markdown 文件
# ## 分类1
# - [链接1](https://example1.com)

uv run linkding-tools upload-markdown mylinks.md
```

## 配置详解

### 配置优先级

工具按以下优先级加载配置：
1. **环境变量**（最高）- `LINKDING_URL` 和 `LINKDING_TOKEN`
2. **.env 文件** - 项目根目录的 `.env` 文件
3. **交互式提示**（最低）- 缺失时自动提示

### 不同场景的配置方式

| 场景 | 推荐方式 | 示例 |
|------|----------|------|
| 本地开发 | .env 文件 | `uv run linkding-tools setup-config` |
| CI/CD | 环境变量 | `export LINKDING_URL=... LINKDING_TOKEN=...` |
| Docker | 环境变量 | `docker run -e LINKDING_URL=...` |
| 首次使用 | 交互式 | `uv run linkding-tools setup-config` |

### 配置命令

```bash
# 交互式配置向导
uv run linkding-tools setup-config

# 验证配置有效性
uv run linkding-tools test-config

# 查看当前配置（Token 被屏蔽）
uv run linkding-tools show-config
```

## 获取 API Token

1. 登录到你的 Linkding 实例
2. 点击右上角用户头像，选择"Settings"或"设置"
3. 在"API"或"API Token"部分，生成或复制你的 token
4. 保存到 `.env` 文件中

## 工作流示例

### 场景 1：导入 Chrome 书签

```bash
# 1. 从 Chrome 导出书签为 HTML 文件
# Chrome 菜单 > 书签 > 书签管理器 > 右上角菜单 > 导出书签

# 2. 使用工具导入
python3 linkding-tools.py import-chrome bookmarks.html

# 3. 确认导入
是否开始导入? (y/n): y

# 成功！所有书签已导入，并保留了原有的文件夹结构作为标签
```

### 场景 2：整理 Markdown 笔记并上传

```bash
# 1. 创建 Markdown 文件，按照结构组织链接
# 例如：开发工具.md，包含多个分类

# 2. 上传到 Linkding
python3 linkding-tools.py upload-markdown 开发工具.md

# 3. 链接会自动按照 Markdown 的分级结构打上标签
# 例如：
# - 基础标签：开发工具
# - 多级标签：开发工具 > IDE，开发工具 > 版本控制
```

### 场景 3：批量重命名标签

```bash
# 1. 发现某个标签的名称需要统一
python3 linkding-tools.py rename-tag python Python

# 2. 所有包含 "python" 标签的链接会自动更新为 "Python"
# 如果链接已有 "Python" 标签，则只删除 "python" 标签
```

## 故障排除

### 连接失败

```
✗ API 连接失败: 401
```

**解决方案：**
- 检查 `LINKDING_URL` 是否正确（包括 https://)
- 检查 `LINKDING_TOKEN` 是否过期或有效
- 在 Linkding 设置中重新生成 token

### 导入到一半失败

工具会显示每个链接的处理结果，支持重试：
- 已成功上传的链接不会重复
- 可以删除已上传的部分，然后重新运行
- 使用 `-y` 参数跳过确认，加快重试速度

### JSONL 文件中有无效数据

工具会自动跳过：
- 缺少 `url` 字段的行
- JSON 格式不正确的行
- 无效的 URL

## 文件结构

```
links/
├── linkding-tools.py      # 主工具脚本
├── pyproject.toml         # uv 项目配置
├── .env.example           # 环境变量示例文件
├── README.md              # 本文件
├── bak/                   # 备份的旧脚本
│   ├── convert_to_jsonl.py
│   ├── import_chrome_bookmarks.py
│   ├── rename_tag.py
│   ├── upload_to_linkding.py
│   └── test_parse_bookmarks.py
└── jsonl_output/          # JSONL 格式的链接输出
    ├── 编程语言.jsonl
    ├── 前端.jsonl
    └── ...
```

## 高级用法

### 批量处理

```bash
#!/bin/bash
# 批量上传多个 Markdown 文件

for file in *.md; do
    echo "处理 $file..."
    python3 linkding-tools.py upload-markdown "$file" -y
done
```

### 与其他工具集成

```bash
# 从 URL 列表文件生成 Markdown
# 然后上传到 Linkding

# 或使用管道
cat url_list.txt | python3 linkding-tools.py upload-markdown -
```

## 故障排除

### 连接失败

```bash
# 运行诊断命令
uv run linkding-tools test-config

# 常见问题：
# 1. LINKDING_URL 是否正确（包括 https://）
# 2. LINKDING_TOKEN 是否有效
# 3. 网络连接是否正常
```

### 配置未生效

```bash
# 检查环境变量（优先级更高）
echo $LINKDING_URL
echo $LINKDING_TOKEN

# 清除环境变量
unset LINKDING_URL LINKDING_TOKEN

# 验证配置
uv run linkding-tools show-config
```

### 导入到一半失败

工具会显示每个链接的处理结果：
- 已成功上传的链接不会重复
- 使用 `-y` 参数跳过确认，加快重试

## 项目结构

```
links/
├── src/linkding_tools/          # 主模块
│   ├── __init__.py              # 主要实现
│   └── __main__.py              # 入口点
├── bak/                         # 备份的旧脚本（已排除）
├── tmp/                         # 测试文件（已排除）
├── linkding-tools.py            # 独立运行版本
├── pyproject.toml               # uv 项目配置
├── README.md                    # 本文件
└── .env.example                 # 配置模板
```

## 项目依赖

该项目使用 uv 管理依赖，目前只依赖 Python 标准库：
- `json` - 处理 JSON/JSONL 数据
- `re` - 正则表达式解析
- `http.client` - HTTP 请求
- `ssl` - HTTPS 支持
- `urllib.parse` - URL 解析

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT
