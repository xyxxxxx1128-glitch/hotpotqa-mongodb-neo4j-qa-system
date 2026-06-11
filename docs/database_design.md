# Neo4j 数据库设计

## 1. 数据集

本项目使用 HotpotQA 数据集。HotpotQA 是一个多跳问答数据集，每条数据包含问题、答案、问题类型、难度、上下文文档和支撑事实。

核心字段：

- `id`：问题编号
- `question`：问题文本
- `answer`：答案
- `type`：问题类型，例如 `bridge`、`comparison`
- `level`：问题难度，例如 `easy`、`medium`、`hard`
- `context`：候选上下文文章和句子
- `supporting_facts`：真正支持答案的关键句子

## 2. 图数据库建模

### 节点

| 节点标签 | 含义 | 主要属性 |
|---|---|---|
| `Question` | 问题 | `id`, `text`, `type`, `level` |
| `Answer` | 答案 | `text` |
| `Document` | 上下文文章 | `title` |
| `Sentence` | 文章句子 | `id`, `text`, `sent_id`, `title` |
| `Type` | 问题类型 | `name` |
| `Level` | 问题难度 | `name` |

### 关系

| 关系 | 含义 |
|---|---|
| `(Question)-[:HAS_ANSWER]->(Answer)` | 问题对应答案 |
| `(Question)-[:HAS_CONTEXT]->(Document)` | 问题包含候选上下文文章 |
| `(Document)-[:HAS_SENTENCE]->(Sentence)` | 文章包含句子 |
| `(Question)-[:SUPPORTS]->(Sentence)` | 句子是回答该问题的支撑事实 |
| `(Question)-[:HAS_TYPE]->(Type)` | 问题属于某种类型 |
| `(Question)-[:HAS_LEVEL]->(Level)` | 问题属于某种难度 |

## 3. 多跳查询含义

HotpotQA 的一个问题通常需要结合多个支撑事实才能得到答案。在 Neo4j 中可以表示为：

```text
Question -> Supporting Sentence 1 -> Document 1
Question -> Supporting Sentence 2 -> Document 2
Question -> Answer
```

这样可以通过图路径直观展示推理过程。

## 4. 常用 Cypher

### 关键词检索

```cypher
MATCH (q:Question)
OPTIONAL MATCH (q)-[:HAS_ANSWER]->(a:Answer)
WHERE toLower(q.text) CONTAINS toLower($keyword)
   OR toLower(a.text) CONTAINS toLower($keyword)
RETURN q.id AS id, q.text AS question, a.text AS answer, q.type AS type, q.level AS level
LIMIT 20;
```

### 查询多跳支撑事实

```cypher
MATCH (q:Question {id: $id})-[:SUPPORTS]->(s:Sentence)<-[:HAS_SENTENCE]-(d:Document)
OPTIONAL MATCH (q)-[:HAS_ANSWER]->(a:Answer)
RETURN q, d, s, a;
```

### 按类型聚类统计

```cypher
MATCH (q:Question)
RETURN q.type AS type, count(q) AS count
ORDER BY count DESC;
```

### 按难度聚类统计

```cypher
MATCH (q:Question)
RETURN q.level AS level, count(q) AS count
ORDER BY count DESC;
```
