# README.md
# 本地离线LLM多轮对话机器人
## 项目简介
基于 Python + Ollama 构建的离线聊天机器人，实现**冷热分离会话持久化、SSE流式打字机输出、多模型动态切换、滑动窗口上下文管理、大模型幻觉抑制**。
> 可直接写入简历，支持本地离线运行，预留接口可扩展兼容OpenAI格式云端API。

## ✨项目技术亮点（简历素材）
1. **分层架构设计**：划分为配置层、核心LLM层、会话管理层、存储层、工具层，代码解耦，易于维护扩展；
2. **冷热分离持久化方案**：Redis缓存活跃会话上下文（高速读取、自动过期），MySQL永久归档全部聊天记录；缓存失效自动从数据库加载历史并回填缓存；
3. **统一封装LLM客户端**，原生支持Ollama本地模型，预留扩展点兼容云端大模型API；支持运行时动态切换模型；
4. **SSE流式输出**，控制台实现主流AI产品打字机交互效果；
5. **滑动窗口上下文截断策略**，限制送入模型的对话轮数，控制Token消耗，防止上下文窗口超限；
6. **提示词工程策略**配合调低temperature，缓解大模型幻觉问题；
7. 完善指令交互、参数校验、全局异常捕获，程序容错性强，单次对话异常不会造成整体程序崩溃。

## 📁项目目录结构
```
llm_chatbot/
├── config/                 # 全局配置层
│   ├── __init__.py
│   └── settings.py         # 数据库、Redis、模型参数全部统一配置
├── core/                   # 核心业务层
│   ├── __init__.py
│   ├── llm_client.py       # LLM统一客户端：普通对话 + 流式对话
│   └── session_manager.py  # 会话管理器（多轮对话、持久化、滑动窗口）
├── storage/                # 数据存储层
│   ├── __init__.py
│   ├── redis_cache.py      # Redis会话缓存
│   └── mysql_store.py      # MySQL消息持久化
├── utils/                  # 工具辅助层
│   ├── __init__.py
│   └── logger.py           # 日志模块
├── main.py                 # 程序入口、控制台交互
├── requirements.txt        # 依赖清单
└── README.md               # 部署文档
```

## 🧰环境前置准备
### 1. 启动服务
1. **Ollama**：本地启动，提前拉取模型（示例：`ollama pull qwen2.5:3b-instruct-q4_K_M`）
2. **Redis**：启动 redis-server，版本推荐 `4.6.0`（规避新版协议兼容问题）
3. **MySQL**：启动服务，创建数据库并执行建表SQL

### 2. MySQL建表SQL
```sql
CREATE DATABASE IF NOT EXISTS llm_chat;
USE llm_chat;

CREATE TABLE IF NOT EXISTS chat_session (
    session_id VARCHAR(100) PRIMARY KEY COMMENT '会话唯一ID',
    user_id VARCHAR(100) COMMENT '用户标识',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

CREATE TABLE IF NOT EXISTS chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) COMMENT '关联会话ID',
    role VARCHAR(20) COMMENT 'user / assistant / system',
    content TEXT COMMENT '对话内容',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '消息时间'
);
```

### 3. Python依赖安装
```bash
pip install -r requirements.txt
```
requirements.txt内容：
```txt
requests>=2.31.0
redis==4.6.0
pymysql>=1.1.0
```

## ⚙️配置修改
打开 `config/settings.py`，修改对应连接信息：
- MYSQL_PASSWORD：填写你的MySQL密码
- 可自定义：默认模型、最大对话轮数MAX_TURN、Redis过期时间、temperature温度、系统提示词

## 🚀启动运行
进入项目根目录，执行：
```bash
python main.py
```

## 📝控制台交互指令
```
========== 指令说明 ==========
/new          创建全新会话，生成新session_id
/load sid     加载指定历史会话，例 /load aaaaa-bbbbb-ccccc
/model name   动态切换大模型，例 /model qwen2.5:7b
exit          正常退出程序
==============================
```

## 💡核心机制说明（面试重点）
### 1. 冷热分离原理
- **MySQL**：永久保存全部聊天记录，用于数据归档溯源；
- **Redis**：缓存当前会话上下文，设置2小时TTL；访问速度更快；
- 逻辑：优先读取Redis；缓存失效，自动从MySQL加载历史消息，并回填Redis；
> ⚠️注意：加载历史后会执行**滑动窗口截断**，内存仅保留最近N轮对话送入模型；数据库仍然完整保存所有记录。

### 2. 滑动窗口策略 MAX_TURN=4
一轮对话 = 用户提问 + AI回答（两条消息）
最多保留最近4轮完整问答，system系统提示词永久保留；
对话轮数超出限制，自动删除最早一轮一问一答，控制上下文Token数量。

### 3. 幻觉抑制方案
1. 系统提示词约束：禁止编造事实，不知道直接说明；
2. temperature默认0.2，降低生成随机性；
> 优化方向：后续接入RAG检索增强，从根源大幅缓解幻觉。

## ❗常见问题
1. **Redis内消息没有截断，持续堆积**
> 修复方案：确认`session_manager.py`中，追加assistant回答后执行二次`_truncate_history()`；加载MySQL历史消息后立刻执行截断。
2. **重启程序后AI“失忆”**
> 数据库存在完整记录，但滑动窗口截断久远对话，送入LLM的上下文只有最近N轮；可调大MAX_TURN或者后续接入历史RAG。
3. **提示Ollama未启动**
> 检查ollama服务是否正常运行，确认`settings.py`中OLLAMA_BASE_URL地址无误。
4. **MySQL连接报错**
> 核对账号、密码、端口，确认数据库`llm_chat`已经创建。

## 📌拓展优化方向（后续迭代）
1. 将日志持久化写入本地文件；
2. 接入RAG向量数据库，实现长期对话记忆；
3. 增加Redis用户限流；
4. 封装Web服务，提供HTTP流式接口；
5. 支持多用户隔离管理。

## 📌演示录制建议（面试展示素材）
推荐录屏流程：
1. 启动程序，展示自动生成会话ID；
2. 多轮流式对话，演示打字机效果；
3. 使用`/new`新建会话；
4. exit退出程序，重新启动，使用`/load + session_id`恢复历史会话；
5. 使用`/model`指令动态切换模型。
