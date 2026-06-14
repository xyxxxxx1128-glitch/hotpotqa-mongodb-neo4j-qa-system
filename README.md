# MongoDB + Neo4j HotpotQA 多跳问答系统

本项目用于课程作业：选择课程数据库 MongoDB 与 Neo4j 管理 HotpotQA 多跳问答数据集，并建立网页支持多跳过程查询、关键词检索、简单聚类和可视化。

## 项目定位

本项目采用混合数据库架构：

- MongoDB：存储完整 HotpotQA 原始记录，包括问题、答案、上下文、候选句子和支撑事实
- Neo4j：存储多跳推理关系骨架，包括问题、答案、文档和支撑事实句子
- FastAPI：统一提供检索、聚类、多跳路径查询接口
- GitHub Pages：托管前端网页

实验版本计划导入 HotpotQA `distractor` 配置中的 10000 条真实数据。

## 为什么使用混合架构

HotpotQA 的 `context` 字段包含大量候选文章和句子。如果全部写入 Neo4j，会占用较多空间。混合架构的分工更合理：

| 数据库 | 保存内容 | 作用 |
|---|---|---|
| MongoDB | 完整 HotpotQA JSON 原始数据 | 检索、详情、聚类统计 |
| Neo4j | 问题、答案、文档、支撑事实关系 | 多跳路径查询和图谱可视化 |

这样既保留完整数据，又降低 Neo4j 的存储压力。

## 功能

- 导入 10000 条真实 HotpotQA 数据
- MongoDB 保存完整问答记录
- Neo4j 构建多跳问答知识图谱
- 关键词检索问题和答案
- 查询问题的多跳支撑事实路径
- 按类型和难度进行简单聚类
- 使用 ECharts 展示图谱和统计图
- GitHub Pages 静态托管前端页面

## 技术选型

| 模块 | 技术 |
|---|---|
| 文档数据库 | MongoDB |
| 图数据库 | Neo4j |
| 数据处理 | Python |
| 后端 | FastAPI |
| 前端 | HTML + JavaScript + ECharts |
| 前端部署 | GitHub Pages |

## 快速运行

### 1. 创建虚拟环境

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止启用脚本：

```bash
.\.venv\Scripts\activate.bat
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

复制 `.env.example` 为 `.env`：

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=你的Neo4j密码
NEO4J_DATABASE=neo4j

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=hotpotqa
MONGODB_COLLECTION=questions

CORS_ORIGINS=*
```

### 4. 导入数据

先导入示例数据检查链路：

```bash
python scripts/import_sample.py
```

正式导入 10000 条 HotpotQA 真实数据：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear
```

如果当前网络无法访问 Hugging Face，可以先手动下载 HotpotQA 的 `.parquet` 或 `.json` 文件，再从本地文件导入：

```bash
python scripts/import_hotpotqa.py --data-file path\to\hotpotqa.parquet --limit 10000 --clear
```

默认情况下：

- MongoDB 保存完整 HotpotQA 记录
- Neo4j 只保存支撑事实相关句子和图关系

如果要让 Neo4j 也保存全部候选 context 句子：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear --include-all-context
```

### 5. 查看统计

```bash
python scripts/neo4j_stats.py
```

### 6. 启动后端

```bash
uvicorn backend.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

### 7. 导出 GitHub Pages 静态展示数据

```bash
python scripts/export_static_data.py --limit 50
```

然后推送：

```bash
git add .
git commit -m "Use MongoDB and Neo4j hybrid HotpotQA architecture"
git push
```

## 前端

前端位于 `frontend/`，已配置 GitHub Actions 自动发布到 GitHub Pages。

如果后端部署到云端，只需要改：

```js
// frontend/config.js
window.API_BASE = "https://你的后端地址";
```

## 课程报告口径

可以这样描述：

```text
本系统采用 MongoDB + Neo4j 混合架构。MongoDB 保存 HotpotQA 完整原始数据，Neo4j 保存多跳推理所需的图关系。受免费云数据库容量限制，实验版本导入 10000 条真实 HotpotQA 数据进行展示；导入脚本支持调整 limit 或导入完整 split。
```
