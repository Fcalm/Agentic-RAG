# Agentic-RAG

一个开箱即用的 **Agentic RAG 知识库问答系统**：上传你的文档，像聊天一样提问，AI 会自动检索、验证、重写查询并给出带引用来源的回答，全过程实时可视化。

> 技术栈一句话：FastAPI + LangChain/LangGraph Agent 后端 · Milvus 混合检索 · PostgreSQL + Redis 存储 · Vue 3 + TypeScript 前端。

---

## 1. 它能帮你做什么？

### 核心场景：把一堆文档变成一个「懂你资料的问答助手」

| 你想做的事 | Agentic-RAG 帮你做到 |
|---|---|
| 上传 PDF / Word / Excel 资料，之后直接提问 | ✅ 拖拽上传即可，文档自动切分、向量化入库 |
| 问一个复杂问题，希望答案准确、有依据 | ✅ AI 自动把复杂问题拆成多个子问题并行检索，最后汇总去重 |
| 担心 AI "一本正经地胡说" | ✅ 每条证据先经过相关性评分，证据不足时会自动换一种问法重新检索，而不是硬编答案 |
| 回答里要有出处，方便核实 | ✅ 每条回答附带引用来源卡片（含相似度得分、所在页码） |
| 看不懂 AI "中间在干嘛" | ✅ 检索 → 评估 → 重写 → 回答的每一步都在界面上实时展示，像看 AI 思考过程 |
| 答案跑偏了想立刻停下来 | ✅ 回答过程中可随时一键终止，立刻停止生成 |
| 多轮对话要记得上文 | ✅ 自动摘要历史对话，长对话也不丢上下文 |
| 无需登录、多人共用 | ✅ 开箱即用的共享知识库与会话工作区 |

### 一个典型问答背后发生了什么

```
你提问 ──► 判断问题复杂度 ──► 拆解子问题 ──► 并行检索知识库
       ──► 评估证据是否够用 ──► 不够？自动重写问题再检索一次
       ──► 精排过滤噪音 ──► 流式生成回答 + 引用来源
```

对用户来说只需一步：**输入问题，等答案**。其余全部自动完成，且每一步可见、可追踪（可选接入 LangSmith 做全链路追踪）。

## 2. 快速开始（约 10 分钟）

前提：装好 **Docker**（用来一键启动数据库等依赖）。

### 第 1 步：启动依赖服务（PostgreSQL / Redis / Milvus）

```bash
docker compose up -d
```

### 第 2 步：配置模型密钥

复制 `.env.example` 为 `.env`，填入你的模型服务信息（任何兼容 OpenAI 接口的服务均可）：

```bash
ARK_API_KEY=你的API密钥
MODEL=主对话模型名
FAST_MODEL=轻量模型名     # 负责问题拆解和重写
GRADE_MODEL=评判模型名     # 负责证据评分
BASE_URL=模型服务地址
```

> 首次运行会自动从 Hugging Face 下载本地 Embedding 模型（默认 `BAAI/bge-m3`），国内网络已在 `.env.example` 里配好镜像加速。

### 第 3 步：启动后端

```bash
uv sync                # 安装 Python 依赖
uv run python backend/app.py
```

后端运行在 http://localhost:8000 ，并直接托管编译好的前端页面。

### 第 4 步：打开页面，开始使用

浏览器访问 **http://localhost:8000** ：

1. 在右侧「知识库」面板上传你的文档，等待向量化完成；
2. 在左侧新建会话，直接提问；
3. 观察"思考中"气泡里的检索步骤，展开回答下方的引用卡片核对来源。

想改界面或做前端开发？进入 `frontend/` 目录运行 `npm install && npm run dev`，开发模式运行在 http://localhost:3000 。

---

## 3. 环境要求

| 组件 | 版本要求 | 用途 |
|---|---|---|
| Python | ≥ 3.12 | 后端运行时 |
| uv | 最新版 | Python 依赖管理（仓库含 `uv.lock`） |
| Node.js | ≥ 18 | 前端构建（Vite 4 + Vue 3 + TS） |
| Docker & Docker Compose | 稳定版 | 启动 PostgreSQL 15 / Redis 7 / Milvus 2.5+（etcd + MinIO + Attu） |

模型侧要求：任一 OpenAI 兼容 API（对话 / FAST / GRADE 三个模型角色）；Embedding 默认本地运行 `BAAI/bge-m3`（1024 维，CPU 可跑）；Rerank 可选（不配置自动降级）。

## 4. 运行命令

```bash
# 1) 基础设施：PostgreSQL + Redis + Milvus 全家桶（etcd/MinIO/Attu）
docker compose up -d

# 2) 后端
uv sync                            # 安装依赖
cp .env.example .env               # 填写模型密钥等配置
uv run python backend/app.py       # 或: uv run uvicorn backend.app:app --reload
# 后端默认 0.0.0.0:8000，由 FastAPI 静态托管 frontend/dist

# 3) 前端（开发模式）
cd frontend
npm install
npm run dev                        # http://localhost:3000，API 代理到 8000
npm run build                      # 产物输出 frontend/dist/，供后端静态托管
npm run test                       # Vitest 单元测试

# 4) 后端测试
uv run pytest tests/
```

常用运维入口：

- Attu（Milvus 可视化控制台）：http://localhost:8080
- MinIO 控制台：http://localhost:9001 （minioadmin / minioadmin）
- LangSmith 追踪：在 `.env` 配置 `LANGSMITH_API_KEY` 后自动开启全部 LangChain/LangGraph 上报

## 5. 项目架构

### 目录结构

```
Agentic-RAG/
├── backend/                  # FastAPI 后端（分层包结构，统一 from backend.xxx import）
│   ├── app.py                # 入口：CORS、静态资源挂载、uvicorn 启动
│   ├── api/                  # HTTP 层：路由聚合与 sessions/chat/documents 路由
│   ├── chat/                 # 对话域：service / runtime / request_context / storage
│   ├── rag/                  # RAG 核心：pipeline.py（LangGraph 工作流）、utils.py（混合检索/精排）
│   ├── indexing/             # 入库链路：分块、Embedding、Milvus 读写、父块 DocStore
│   ├── tools/                # LangChain @tool（知识库检索、天气示例）
│   ├── infra/                # database.py / cache.py（PG、Redis 连接）
│   ├── db/                   # SQLAlchemy ORM 模型
│   ├── schemas/              # Pydantic 请求/响应模型
│   └── jobs/                 # 异步上传/删除任务进度
├── frontend/                 # Vite + Vue 3 + TS + Pinia
│   ├── stores/               # sessions / chat / documents 三大状态仓库
│   ├── components/           # ThinkingTrace / References / UploadSection 等
│   └── utils/api.ts          # fetch ReadableStream 解析 SSE + AbortController
├── tests/                    # 后端测试
├── docker-compose.yml        # PG + Redis + Milvus(etcd/MinIO/Attu)
├── .env.example              # 全量环境变量模板
└── langsmith_eval.py         # LangSmith 评估脚本
```

### 请求链路（端到端）

```
前端提问
  └► POST /chat/stream (SSE, StreamingResponse)
        └► chat_with_agent_stream()
              ├► 创建 ChatRequestContext（每请求隔离：RAG step / trace / 工具预算）
              ├► create_agent_for_request(ctx) 绑定专属工具
              └► 后台任务 agent.astream(stream_mode="messages") 逐 token 产出
                    └► Agent 按意图路由：
                         ├─ 天气类 → get_current_weather 工具
                         └─ 知识类 → search_knowledge_base → LangGraph RAG 工作流
                              （节点通过 loop.call_soon_threadsafe 跨线程实时推送进度）
  └► SSE 混合事件流：{type: rag_step} + {type: content} → 前端状态机渲染
  └► 消息落库 PostgreSQL，Redis 缓存热点会话
```

### RAG 工作流（LangGraph）

```
classify_complexity（本地规则直判 simple，其余 FAST_MODEL 一次完成判断 + 拆出 2-4 个子问题）
        │
   ┌────┴─────────────┐
 simple              complex ──► LangGraph Send 并行子 Agent：检索 → 证据评判 → synthesis 去重
   └────┬─────────────┘
        ▼
retrieve_initial：L3 叶子层 Milvus Hybrid 检索（Dense + 原生 BM25 Sparse，RRF k=60 融合）
        → Auto-merging（L3→L2→L1 向上合并父块，阈值门控）
        → Jina Rerank 精排 + RERANK_MIN_SCORE 过滤
        ▼
grade_documents（GRADE_MODEL 结构化输出：相关性 / 可回答性 / 歧义 / route）
        ▼
证据不足 → rewrite_question（FAST_MODEL 单选 Step-back 或 HyDE，只执行一次）
        → retrieve_rewritten → 复评
        ▼
Agent 流式生成最终回答，rag_trace 全程记录可观测
```

### 文档入库链路

```
上传 PDF/Word/Excel → 三级滑动窗口分块（L1/L2/L3，带层级元数据）
  → L1/L2 父块写 PostgreSQL DocStore
  → L3 叶子块：本地 bge-m3 稠密向量 + 原文写入绑定 chinese analyzer 的 text 字段
  → Milvus 2.5+ 服务端 FunctionType.BM25 自动提取稀疏向量（零客户端统计）
  → 重复上传触发事务级清理（Milvus + PG + Redis 同步删除，无悬空数据）
```

## 6. 技术总结

**检索侧**

- **三级分块 + Auto-merging + Leaf-only 索引**：仅叶子块（L3）向量化入库，父块（L1/L2）存 DocStore；召回后按阈值向上合并恢复上下文，兼顾召回粒度与回答上下文完整性。
- **Hybrid Search 双塔混合检索**：稠密路径（`HuggingFaceEmbeddings` + bge-m3，IP 度量）与稀疏路径（Milvus 服务端原生 BM25）通过 `AnnSearchRequest` 并发发起，`RRFRanker(k=60)` 无参数化融合，兼顾语义与词面匹配。

**Agent 侧**

- **自适应复杂度规划**：明显的单事实问题由本地规则直判，零模型调用；其余由 FAST_MODEL 一次结构化调用完成复杂度判断与子问题拆解，控制最坏延迟。
- **并行 Sub-Agent**：复杂问题通过 LangGraph `Send` API 并行执行多个子问题的"检索 → 评判"，避免嵌套图与串行等待。
- **Corrective RAG**：独立的 GRADE_MODEL 做结构化证据评判（相关性/可回答性/歧义/路由）；证据不足时 FAST_MODEL 单选 Step-back 或 HyDE，只做一次重写检索 + 一次复评，避免重写循环。

**关键环境变量分组**：模型（`MODEL` / `FAST_MODEL` / `GRADE_MODEL` / `BASE_URL` / `ARK_API_KEY`）、向量（`EMBEDDING_MODEL` / `DENSE_EMBEDDING_DIM`）、检索（`RETRIEVAL_*` / `AUTO_MERGE_*` / `RERANK_*`）、基础设施（`MILVUS_*` / `DATABASE_URL` / `REDIS_URL`），完整清单见 [.env.example](.env.example)。
