# 部署说明

## 1. Neo4j

可以选择本地 Neo4j 或 Neo4j AuraDB。

### 本地 Neo4j

1. 安装 Neo4j Desktop
2. 创建数据库
3. 启动数据库
4. 记录连接信息：

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=你的密码
NEO4J_DATABASE=neo4j
```

### Neo4j AuraDB

1. 进入 Neo4j Aura 官网
2. 创建免费实例
3. 下载或复制连接信息
4. 将 `.env` 中的连接信息替换为 AuraDB 提供的 URI、用户名和密码

## 2. 后端 FastAPI

### 本地运行

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

### Render 部署

Render Web Service 可使用：

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

需要在 Render 的环境变量里配置：

```text
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
NEO4J_DATABASE
CORS_ORIGINS
```

`CORS_ORIGINS` 填写你的 GitHub Pages 地址，例如：

```text
https://你的用户名.github.io
```

## 3. 前端 GitHub Pages

前端文件在 `frontend/` 目录。

如果只做静态演示，直接把仓库上传 GitHub。项目已经提供 `.github/workflows/pages.yml`，它会在推送到 `main` 分支后自动把 `frontend/` 发布到 GitHub Pages。

GitHub 仓库设置中需要进入：

```text
Settings -> Pages -> Source -> GitHub Actions
```

如果后端已经部署，需要在 `frontend/app.js` 中修改：

```js
const API_BASE = "https://你的后端地址";
```

## 4. GitHub 上传命令

```bash
git init
git add .
git commit -m "Initial Neo4j HotpotQA project"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

## 5. 答辩展示建议

展示顺序：

1. 说明 HotpotQA 是数据集，Neo4j 是课程数据库
2. 展示 Neo4j 中的问题、文档、句子、答案节点
3. 展示网页关键词检索
4. 点击一个问题，展示多跳支撑事实路径
5. 展示类型和难度聚类统计图
6. 展示 GitHub Pages 页面和代码仓库
