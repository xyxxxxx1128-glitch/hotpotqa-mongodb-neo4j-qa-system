# 基于 MongoDB 与 Neo4j 的 HotpotQA 多跳问答查询与可视化系统

## 1. 项目背景

多跳问答任务需要结合多个文档或多个事实才能得到答案。HotpotQA 数据集中不仅包含问题和答案，还包含上下文文档、候选句子和支撑事实。单一数据库不一定适合同时处理完整文档存储和多跳关系查询，因此本项目采用 MongoDB 与 Neo4j 的混合架构。

## 2. 数据集介绍

本项目使用 HotpotQA 数据集。HotpotQA 不是数据库，而是多跳问答数据集。每条数据包含：

- `question`：问题
- `answer`：答案
- `context`：上下文文档和候选句子
- `supporting_facts`：支撑答案的关键事实
- `type`：问题类型
- `level`：问题难度

实验版本导入 HotpotQA `distractor` 配置中的 10000 条真实数据。

## 3. 数据库选择

本项目选择课程中的 MongoDB 和 Neo4j：

- MongoDB 适合保存 HotpotQA 的完整 JSON 原始结构
- Neo4j 适合表达问题、文档、支撑事实和答案之间的多跳关系

混合架构既保留完整数据，又能直观展示多跳推理路径。

## 4. 数据规模与存储策略

免费云数据库容量有限，不适合完整承载 HotpotQA 全量数据。为保证课程展示稳定性，本项目导入 10000 条真实 HotpotQA 数据。

存储策略：

- MongoDB 保存完整 HotpotQA 原始记录
- Neo4j 默认只保存多跳推理所需的支撑事实句子和关系
- 非支撑事实的候选句子保留在 MongoDB 中
- 如需完整图谱，可通过参数 `--include-all-context` 导入全部候选句子到 Neo4j

## 5. 数据模型设计

### 5.1 MongoDB

MongoDB 中每条数据对应一个文档，保存完整字段：

```json
{
  "id": "...",
  "question": "...",
  "answer": "...",
  "type": "bridge",
  "level": "medium",
  "context": {...},
  "supporting_facts": {...}
}
```

MongoDB 用于关键词检索、完整详情查询和聚类统计。

### 5.2 Neo4j

Neo4j 节点：

- `Question`
- `Answer`
- `Document`
- `Sentence`
- `Type`
- `Level`

Neo4j 关系：

- `HAS_ANSWER`
- `HAS_CONTEXT`
- `HAS_SENTENCE`
- `SUPPORTS`
- `HAS_TYPE`
- `HAS_LEVEL`

多跳路径示例：

```text
Question -> Supporting Sentence 1 -> Document 1
Question -> Supporting Sentence 2 -> Document 2
Question -> Answer
```

## 6. 系统实现

| 模块 | 实现 |
|---|---|
| 文档数据存储 | MongoDB |
| 图关系存储 | Neo4j |
| 数据处理 | Python |
| 后端接口 | FastAPI |
| 前端页面 | HTML + JavaScript + ECharts |
| 前端托管 | GitHub Pages |

Python 脚本负责读取 HotpotQA 数据并同时写入 MongoDB 和 Neo4j。FastAPI 提供统一接口。前端使用 ECharts 展示图谱和统计图。

## 7. 功能实现

### 7.1 关键词检索

用户输入关键词后，系统在 MongoDB 中检索问题文本、答案、类型和难度。

### 7.2 多跳过程查询

用户点击问题后，系统从 Neo4j 查询该问题对应的支撑事实句子、文档和答案，并用图结构展示推理路径。

### 7.3 简单聚类

系统在 MongoDB 中按问题类型和难度进行统计：

- 类型：`bridge`、`comparison`
- 难度：`easy`、`medium`、`hard`

### 7.4 可视化

前端使用 ECharts：

- 图谱图展示问题、文档、支撑事实和答案之间的关系
- 柱状图展示类型和难度聚类结果

## 8. 部署方式

前端部署到 GitHub Pages。后端和数据库可本地运行；如果需要实时云端查询，可将 FastAPI 部署到 Render，将 MongoDB 部署到 MongoDB Atlas，将 Neo4j 部署到 Neo4j AuraDB。

考虑到免费云数据库容量限制，本项目课程展示优先采用本地数据库导入数据，并导出真实样例数据到 GitHub Pages 静态页面展示。

## 9. 总结

本项目使用 MongoDB 与 Neo4j 混合管理 HotpotQA 多跳问答数据。MongoDB 保存完整原始数据，Neo4j 保存多跳推理关系，完成了数据导入、关键词检索、多跳路径查询、简单聚类统计和网页可视化。该方案比单独使用 Neo4j 存储全部文本更节省图数据库空间，也更符合不同数据库的特点。
