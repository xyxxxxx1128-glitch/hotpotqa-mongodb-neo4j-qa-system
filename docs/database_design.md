# MongoDB + Neo4j 数据库设计

## 1. 数据集

本项目使用 HotpotQA 数据集。HotpotQA 是多跳问答数据集，每条数据包含问题、答案、问题类型、难度、上下文文档、候选句子和支撑事实。

数据来源：

```text
https://huggingface.co/datasets/hotpotqa/hotpot_qa
```

本项目使用 `distractor` 配置。该配置原始规模约为：

```text
train: 90447 条
validation: 7405 条
总计: 97852 条
```

实验版本从训练集文件中导入前 10000 条真实数据。这样可以在本地资源可控的情况下，完成 MongoDB 与 Neo4j 的建模、检索、多跳查询、聚类和可视化验证。导入脚本支持通过 `--limit` 调整导入数量，也支持不设置 `--limit` 时导入完整 split。

## 2. 混合数据库分工

| 数据库 | 保存内容 | 作用 |
|---|---|---|
| MongoDB | 完整 HotpotQA JSON 原始记录 | 检索、详情展示、聚类统计 |
| Neo4j | 问题、答案、文档、支撑事实关系 | 多跳路径查询、图谱可视化 |

这种设计避免把所有候选句子都写入 Neo4j，降低图数据库体积。

## 3. MongoDB 文档结构

MongoDB 中每条 HotpotQA 数据作为一个文档保存：

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

MongoDB 主要用于：

- 按关键词检索问题和答案
- 获取完整上下文
- 按 `type` 和 `level` 聚类统计

## 4. Neo4j 图模型

### 节点

| 节点标签 | 含义 | 主要属性 |
|---|---|---|
| `Question` | 问题 | `id`, `text`, `type`, `level` |
| `Answer` | 答案 | `text` |
| `Document` | 上下文文章 | `title` |
| `Sentence` | 支撑事实句子 | `id`, `text`, `sent_id`, `title` |
| `Type` | 问题类型 | `name` |
| `Level` | 问题难度 | `name` |

### 关系

| 关系 | 含义 |
|---|---|
| `(Question)-[:HAS_ANSWER]->(Answer)` | 问题对应答案 |
| `(Question)-[:HAS_CONTEXT]->(Document)` | 问题涉及上下文文章 |
| `(Document)-[:HAS_SENTENCE]->(Sentence)` | 文档包含支撑事实句子 |
| `(Question)-[:SUPPORTS]->(Sentence)` | 句子支持回答该问题 |
| `(Question)-[:HAS_TYPE]->(Type)` | 问题类型 |
| `(Question)-[:HAS_LEVEL]->(Level)` | 问题难度 |

## 5. 多跳路径

```text
Question -> Supporting Sentence 1 -> Document 1
Question -> Supporting Sentence 2 -> Document 2
Question -> Answer
```

前端图谱展示的就是该路径。

## 6. 存储优化

默认导入时：

- MongoDB 保存完整 `context`
- Neo4j 只保存 `supporting_facts` 对应的支撑事实句子

如果需要完整图谱，可使用：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear --include-all-context
```
