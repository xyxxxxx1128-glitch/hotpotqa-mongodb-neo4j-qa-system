# 基于 Neo4j 的 HotpotQA 多跳问答知识图谱查询与可视化系统

## 1. 项目背景

多跳问答任务需要综合多个文档或多个事实才能得到答案。传统表结构不容易直观表达问题、文档、句子和答案之间的关系。Neo4j 图数据库适合管理关系密集型数据，因此本项目选择 Neo4j 管理 HotpotQA 数据集，并通过网页展示多跳查询、检索、聚类和可视化结果。

## 2. 数据集介绍

本项目使用 HotpotQA 数据集。HotpotQA 不是数据库，而是多跳问答数据集。每条数据包含问题、答案、上下文文章、候选句子、支撑事实、问题类型和难度。

主要字段：

- `question`：问题
- `answer`：答案
- `context`：上下文文章和句子
- `supporting_facts`：支撑答案的关键事实
- `type`：问题类型
- `level`：问题难度

## 3. 数据库选择

本项目选择课程中的 Neo4j 图数据库。选择原因：

- HotpotQA 包含问题、文章、句子、答案之间的复杂关系
- Neo4j 可以用节点和边表示多跳推理路径
- Cypher 查询语言适合表达路径查询
- 图可视化结果直观，适合作业展示

## 4. 数据模型设计

节点包括：

- `Question`
- `Answer`
- `Document`
- `Sentence`
- `Type`
- `Level`

关系包括：

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

## 5. 系统实现

系统分为四个部分：

| 模块 | 实现 |
|---|---|
| 数据处理 | Python |
| 数据库 | Neo4j |
| 后端接口 | FastAPI |
| 前端页面 | HTML + JavaScript + ECharts |

Python 脚本负责读取 HotpotQA 数据并导入 Neo4j。FastAPI 负责提供检索、多跳路径和聚类统计接口。前端使用 ECharts 展示图谱和统计图。

## 6. 功能实现

### 6.1 关键词检索

用户输入关键词后，系统在问题文本和答案文本中检索相关记录，并展示问题、答案、类型和难度。

### 6.2 多跳过程查询

用户点击某个问题后，系统查询该问题的支撑事实句子、所属文章和答案，并用图结构展示推理路径。

### 6.3 简单聚类

系统按问题类型和问题难度进行聚类统计：

- 按类型：`bridge`、`comparison`
- 按难度：`easy`、`medium`、`hard`

### 6.4 可视化

前端使用 ECharts：

- 图谱图展示 `Question`、`Document`、`Sentence`、`Answer`
- 柱状图展示类型和难度聚类结果

## 7. 部署方式

前端部署到 GitHub Pages。后端可以部署到 Render 或 Railway，也可以本地运行。数据库可以使用本地 Neo4j 或 Neo4j AuraDB。

## 8. 总结

本项目使用 Neo4j 管理 HotpotQA 多跳问答数据，完成了数据导入、关键词检索、多跳路径查询、简单聚类统计和网页可视化。通过图数据库，问题、文档、句子和答案之间的关系可以被直观表示，符合多跳问答数据的特点。
