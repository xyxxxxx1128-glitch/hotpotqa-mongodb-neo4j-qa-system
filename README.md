# HotpotQA MongoDB + Neo4j 多跳问答系统

这是一个基于 **MongoDB + Neo4j** 的 HotpotQA 多跳问答数据管理与可视化项目。系统已经导入 10000 条真实 HotpotQA 数据，并将其中 500 条真实样例导出到 GitHub Pages 前端用于在线展示。

## 在线前端

前端页面通过 GitHub Pages 托管。

如果仓库名为 `hotpotqa-mongodb-neo4j-qa-system`，访问：

```text
https://xyxxxxx1128-glitch.github.io/hotpotqa-mongodb-neo4j-qa-system/
```


也可以在 GitHub 仓库中进入：

```text
Settings -> Pages
```

页面中 `Your site is live at ...` 后面的链接就是当前前端地址。

## 项目功能

系统支持以下功能：

- **关键词检索**：输入关键词，检索 HotpotQA 问题、答案、类型和难度。
- **多跳路径展示**：点击问题后，展示该问题对应的支撑事实句子、来源文档和答案。
- **图谱可视化**：用 ECharts 展示 `Question -> Document -> Sentence -> Answer` 的多跳关系图。
- **简单聚类统计**：按问题类型 `bridge / comparison` 和难度 `easy / medium / hard` 统计并绘制柱状图。
- **静态在线展示**：GitHub Pages 直接展示从真实数据库导出的 500 条样例，不依赖本地服务。
- **本地实时查询**：本地运行 FastAPI 后，可以实时查询 MongoDB 和 Neo4j。

## 数据库架构

本项目使用混合数据库架构：

| 数据库 | 存储内容 | 用途 |
|---|---|---|
| MongoDB | 完整 HotpotQA 原始记录，包括 question、answer、context、supporting_facts | 检索、详情、聚类统计 |
| Neo4j | 问题、答案、文档、支撑事实句子之间的图关系 | 多跳路径查询和图谱可视化 |

这样做的原因是：HotpotQA 的 `context` 字段包含大量候选文章和句子，如果全部写入 Neo4j 会占用较多空间。MongoDB 更适合保存完整 JSON 原始数据，Neo4j 更适合保存多跳推理关系。

## 当前数据规模

数据来源：

- HotpotQA Hugging Face 数据集页面：https://huggingface.co/datasets/hotpotqa/hotpot_qa
- 本项目使用 `distractor` 配置下的训练数据文件 `train-00000-of-00002.parquet`

HotpotQA `distractor` 配置的原始规模约为：

```text
train: 90447 条
validation: 7405 条
总计: 97852 条
```

本实验没有直接导入完整数据集，而是取前 10000 条真实样本进行系统构建和展示。原因是：

- 课程作业重点是验证数据库建模、查询、聚类和可视化流程，不需要全量数据才能展示功能。
- 免费云数据库容量有限，不适合承载完整 HotpotQA 数据。
- 本地全量导入会占用更多磁盘空间和导入时间。
- 10000 条已经能形成较大规模图谱，足以展示多跳关系查询、检索和统计效果。
- 导入脚本支持调整 `--limit`，也支持不设置 `--limit` 时导入完整 split。

本地实验已导入：

```text
MongoDB documents: 10000

Neo4j nodes:
Question: 10000
Answer: 7757
Document: 87251
Sentence: 22482
Type: 2
Level: 3

Neo4j relationships:
HAS_ANSWER: 10000
HAS_CONTEXT: 99410
HAS_LEVEL: 10000
HAS_SENTENCE: 22482
HAS_TYPE: 10000
SUPPORTS: 23903
```

GitHub Pages 前端使用 `frontend/sample-data.js` 中导出的 500 条真实样例数据进行静态展示。

## 技术栈

| 模块 | 技术 |
|---|---|
| 文档数据库 | MongoDB |
| 图数据库 | Neo4j |
| 数据处理 | Python |
| 后端接口 | FastAPI |
| 前端页面 | HTML + JavaScript + ECharts |
| 静态托管 | GitHub Pages |

## 本地运行

### 1. 准备数据库

需要本地启动：

- MongoDB，默认地址：`mongodb://localhost:27017`
- Neo4j，默认地址：`bolt://127.0.0.1:7687`

`.env` 示例：

```text
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=你的Neo4j密码
NEO4J_DATABASE=neo4j

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=hotpotqa
MONGODB_COLLECTION=questions

CORS_ORIGINS=*
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 PowerShell 阻止启用脚本：

```bash
.\.venv\Scripts\activate.bat
```

### 3. 导入 10000 条数据

如果网络可以访问 Hugging Face：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear
```

如果已经下载了 parquet 文件：

```bash
python scripts/import_hotpotqa.py --data-file data\train-00000-of-00002.parquet --limit 10000 --clear
```

默认导入策略：

- MongoDB 保存完整 HotpotQA 记录。
- Neo4j 只保存支撑事实句子和图关系，降低图数据库占用。

### 4. 查看统计

```bash
python scripts/neo4j_stats.py
```

### 5. 启动后端

```bash
uvicorn backend.main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

### 6. 导出静态前端数据

```bash
python scripts/export_static_data.py --limit 500
```

导出后提交：

```bash
git add .
git commit -m "Update real HotpotQA frontend data"
git push
```

GitHub Actions 会自动重新部署 GitHub Pages。

## 目录说明

```text
backend/        FastAPI 后端和 MongoDB/Neo4j 客户端
scripts/        数据导入、统计、静态数据导出脚本
frontend/       GitHub Pages 前端页面
docs/           报告、数据库设计和部署说明
data/           本地数据文件目录，parquet 文件不会提交到 GitHub
```

## 说明

GitHub Pages 是静态托管，因此线上页面默认展示 `frontend/sample-data.js` 中导出的真实样例数据。若要让网页实时查询数据库，需要额外部署 FastAPI 后端，并将 MongoDB 和 Neo4j 部署到云端。
