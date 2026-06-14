# 部署说明

## 1. 数据库

本项目使用 MongoDB + Neo4j 混合架构。

### MongoDB

可以使用本地 MongoDB，也可以使用 MongoDB Atlas。课程作业本地演示时，建议先用本地 MongoDB。

默认连接：

```text
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=hotpotqa
MONGODB_COLLECTION=questions
```

### Neo4j

使用 Neo4j Desktop 创建本地实例，例如 `hotpotqa-db`，启动后记录连接信息：

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=你的密码
NEO4J_DATABASE=neo4j
```

## 2. Python 虚拟环境

Windows PowerShell：

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 PowerShell 阻止启用脚本，可以使用：

```bash
.\.venv\Scripts\activate.bat
```

macOS / Linux：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. 导入 HotpotQA

先用示例数据检查 Neo4j 连接：

```bash
python scripts/import_sample.py
```

正式导入 10000 条 HotpotQA 真实数据到 MongoDB + Neo4j：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear
```

如果 Hugging Face 访问失败，可以下载数据文件后从本地导入：

```bash
python scripts/import_hotpotqa.py --data-file path\to\hotpotqa.parquet --limit 10000 --clear
```

默认只导入支撑事实句子，用于降低 Neo4j 空间占用。如果要把所有候选 context 句子都写入 Neo4j，使用：

```bash
python scripts/import_hotpotqa.py --limit 10000 --clear --include-all-context
```

如果后续要全量导入 train split，可以不设置 `--limit`：

```bash
python scripts/import_hotpotqa.py --clear
```

继续导入 validation split 时，不要加 `--clear`：

```bash
python scripts/import_hotpotqa.py --split validation
```

注意：`--clear` 会清空 Neo4j 中已有节点和关系。

## 4. 启动后端

```bash
uvicorn backend.main:app --reload
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

## 5. 前端 GitHub Pages

前端文件在 `frontend/` 目录。项目已经提供 `.github/workflows/pages.yml`，推送到 `main` 分支后会自动发布 GitHub Pages。

GitHub 仓库设置中需要进入：

```text
Settings -> Pages -> Source -> GitHub Actions
```

如果后端部署到了云端，只需要修改 `frontend/config.js`：

```js
window.API_BASE = "https://你的后端地址";
```

## 6. Render 后端部署

如果要把 FastAPI 部署到 Render，Web Service 设置如下：

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render 环境变量：

```text
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
NEO4J_DATABASE
CORS_ORIGINS
```

`CORS_ORIGINS` 填 GitHub Pages 地址，例如：

```text
https://xyxxxxx1128-glitch.github.io
```

## 7. 答辩展示建议

展示顺序：

1. 说明 HotpotQA 是数据集，Neo4j 是课程数据库
2. 展示 Neo4j 中的问题、文档、句子、答案节点
3. 展示网页关键词检索
4. 点击一个问题，展示多跳支撑事实路径
5. 展示类型和难度聚类统计图
6. 展示 GitHub Pages 页面和代码仓库
