# 👔 穿搭智能顾问 Agent 系统

基于 LangChain Agent 的智能穿搭推荐系统，整合了 RAG 知识库检索和个性化穿搭方案生成功能。

## 📋 功能特点

### 1. 三个核心工具

**工具1：穿搭知识库检索工具**
- 基于 Chroma 向量库做 RAG 检索
- 返回 Top3 相关穿搭知识
- 自动封装成 LangChain Tool

**工具2：场景体型风格适配工具**
- 内置规则库：场景、体型、性别、风格
- 根据用户特征输出对应穿搭原则
- 支持的场景：通勤、约会、运动、正式、休闲
- 支持的体型：梨形、苹果形、沙漏形、直筒形
- 支持的风格：极简、轻熟、休闲、韩系

**工具3：个性化穿搭方案生成工具**
- 整合工具1 + 工具2 的结果
- 调用通义千问生成结构化穿搭方案
- 输出：单品推荐 + 配色建议 + 搭配技巧

### 2. Agent 智能决策

- 使用 LangChain ZERO_SHOT_REACT_DESCRIPTION
- 温度 0.1，确保输出稳定
- verbose 开启，便于调试
- 异常自动降级为 RAG
- 自主决策是否调用工具、调用哪个

### 3. 双模式接口

**RAG 问答接口** (`/rag/chat`)
- 基于向量库的直接检索
- 适合快速查询穿搭知识

**Agent 智能推荐接口** (`/agent/chat`)
- 智能判断用户需求
- 自主选择工具调用
- 支持复杂穿搭方案生成

### 4. 穿搭方案生成接口** (`/outfit/generate`)
- 结构化表单输入
- 一键生成个性化方案
- 结果清晰展示

## 🚀 快速开始

### 步骤1：安装依赖

```bash
cd agent_system
pip install -r requirements.txt
```

### 步骤2：配置 API 密钥

**方式1：使用 .env 文件（推荐）**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的通义千问 API 密钥
```

**方式2：直接修改 config.py**
打开 `config.py`，找到 `DASHSCOPE_API_KEY` 并填入你的密钥：
```python
DASHSCOPE_API_KEY = "你的真实API密钥"
```

**方式3：启动后在界面中输入**
- 启动系统后，在前端界面的 API Key 输入框中填入密钥

### 步骤3：准备向量数据库

将现有的 Chroma 向量数据库复制到 `agent_system/chroma_db` 目录：
```bash
cp -r 你的chroma_db路径 agent_system/chroma_db
```

或者在 `config.py` 中修改向量数据库路径：
```python
PERSIST_DIRECTORY = "你的chroma_db绝对路径"
```

### 步骤4：启动系统

```bash
python start.py
```

或者直接运行 main.py：
```bash
python main.py
```

### 步骤5：访问系统

- 前端页面：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## 📁 项目结构

```
agent_system/
├── __init__.py          # 包初始化文件
├── config.py            # 配置文件（⚠️ 密钥在此配置）
├── tools.py             # 三个核心工具
├── agent.py             # Agent 初始化和逻辑
├── main.py              # FastAPI 主应用
├── start.py             # 启动脚本
├── requirements.txt     # 依赖包列表
├── .env.example         # 环境变量示例
├── README.md            # 本文件
└── static/              # 前端静态文件
    ├── index.html       # 主页面
    ├── style.css        # 样式文件
    └── script.js        # JavaScript 逻辑
```

## 🔑 密钥填写位置

### 位置1：.env 文件（推荐）

创建 `.env` 文件：
```bash
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
```

### 位置2：config.py 文件

```python
# 第8行左右
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxx"
```

### 位置3：前端界面

启动后，在页面顶部的"通义千问 API Key"输入框中填入。

## 📝 API 接口说明

### 1. Agent 聊天接口
**URL:** `POST /agent/chat`

**请求体:**
```json
{
  "message": "我是个女生，梨形身材，要去约会，想要轻熟风格",
  "api_key": "可选，如已配置可省略"
}
```

**响应:**
```json
{
  "success": true,
  "answer": "根据您的需求，为您推荐以下穿搭方案...",
  "error": null,
  "tool_used": "personalized_outfitfit_generator",
  "intermediate_steps": []
}
```

### 2. RAG 问答接口
**URL:** `POST /rag/chat`

**请求体:**
```json
{
  "query": "春天适合穿什么颜色的衣服",
  "api_key": "可选"
}
```

**响应:**
```json
{
  "success": true,
  "answer": "根据知识库，春天适合穿..."
}
```

### 3. 穿搭方案生成接口
**URL:** `POST /outfit/generate`

**请求体:**
```json
{
  "gender": "女",
  "scene": "约会",
  "body_type": "梨形",
  "style": "轻熟",
  "additional_request": "希望显瘦一点",
  "api_key": "可选"
}
```

**响应:**
```json
{
  "success": true,
  "answer": "【穿搭原则】\n1. ...\n【单品推荐】\n...",
  "error": null
}
```

## 🎨 前端使用说明

### RAG 问答页面
- 用于快速查询穿搭知识
- 直接输入问题即可获得基于知识库的回答

### Agent 智能推荐页面
- **结构化表单：** 选择性别、场景、体型、风格，输入额外需求，点击"生成穿搭方案"
- **智能对话：** 直接在输入框描述需求，Agent 会智能判断并调用合适的工具

## 🛠️ 技术栈

- **后端：** Python + FastAPI
- **Agent 框架：** LangChain
- **向量数据库：** Chroma
- **大模型：** 通义千问（DashScope）
- **前端：** 原生 HTML/CSS/JavaScript

## 📌 注意事项

1. **向量数据库：** 必须先准备好 Chroma 向量数据库，否则 RAG 功能将受限
2. **API 密钥：** 必须配置通义千问 API 密钥才能使用
3. **端口占用：** 默认使用 8000 端口，如需修改请在 `config.py` 中更改 PORT
4. **依赖版本：** 建议严格按照 `requirements.txt` 安装依赖

## 🐛 常见问题

**Q1: 启动时提示找不到 chroma_db？**
A: 检查向量数据库路径，确保 `config.py` 中的 `PERSIST_DIRECTORY` 指向正确的目录

**Q2: API 调用失败？**
A: 检查 API 密钥是否正确，网络是否正常

**Q3: Agent 响应很慢？**
A: 首次调用可能较慢，后续会变快。也可以考虑调整 `config.py` 中的模型参数

**Q4: 如何查看 Agent 的详细执行过程？**
A: 查看 `agent_system.log` 日志文件，或者在 `config.py` 中设置 `VERBOSE = True`

## 📄 许可证

本项目仅供学习和研究使用。
