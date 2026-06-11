# Neo4j HotpotQA 多跳问答知识图谱系统

本项目用于课程作业：选择课程数据库 Neo4j，管理 HotpotQA 多跳问答数据集，并提供网页用于查询、检索、简单聚类和可视化。

## 项目功能

- 使用 Python 读取 HotpotQA 数据集
- 将问题、答案、文章、句子、支撑事实导入 Neo4j
- 使用 FastAPI 提供后端查询接口
- 使用 HTML + JavaScript + ECharts 实现前端展示
- 支持关键词检索、多跳证据路径查询、类型/难度聚类统计和图谱可视化
- 支持 GitHub Pages 静态演示模式

## 技术选型

| 模块 | 技术 |
|---|---|
| 数据库 | Neo4j |
| 数据处理 | Python |
| 后端 | FastAPI |
| 前端 | HTML + JavaScript + ECharts |
| 前端部署 | GitHub Pages |
| 后端部署 | Render / Railway / 本地演示 |
| 数据库部署 | Neo4j AuraDB / 本地 Neo4j |

## 目录结构

```text
.
├── backend/              # FastAPI 后端
├── data/                 # 示例数据和导出数据
├── docs/                 # 作业报告和数据库设计文档
├── frontend/             # GitHub Pages 前端
├── scripts/              # 数据导入、导出脚本
├── .env.example          # 环境变量模板
├── requirements.txt      # Python 依赖
└── README.md             # 项目说明
```

## 快速运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Neo4j

复制 `.env.example` 为 `.env`，填写 Neo4j 连接信息。

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

### 3. 导入示例数据

```bash
python scripts/import_sample.py
```

### 4. 启动后端

```bash
uvicorn backend.main:app --reload
```

后端地址：

```text
http://127.0.0.1:8000
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 5. 打开前端

直接打开：

```text
frontend/index.html
```

或通过项目内置的 GitHub Actions 将 `frontend/` 部署到 GitHub Pages。

## 数据模型

主要节点：

- `Question`：问题
- `Answer`：答案
- `Document`：文章
- `Sentence`：句子
- `Type`：问题类型
- `Level`：问题难度

主要关系：

- `(Question)-[:HAS_ANSWER]->(Answer)`
- `(Question)-[:HAS_CONTEXT]->(Document)`
- `(Document)-[:HAS_SENTENCE]->(Sentence)`
- `(Question)-[:SUPPORTS]->(Sentence)`
- `(Question)-[:HAS_TYPE]->(Type)`
- `(Question)-[:HAS_LEVEL]->(Level)`

## GitHub Pages 静态演示

如果后端暂时没有部署，可以使用 `frontend/sample-data.js` 中的示例数据进行静态演示。这样网页可以直接托管到 GitHub Pages，满足课程展示需求。

如果已经把真实数据导入 Neo4j，可以导出一份静态展示数据：

```bash
python scripts/export_static_data.py
```

脚本会更新 `frontend/sample-data.js`，这样 GitHub Pages 不连接后端也可以展示真实数据的一部分。

## 课程报告

报告模板在：

```text
docs/report.md
```

可以根据实际截图和运行结果补充。
