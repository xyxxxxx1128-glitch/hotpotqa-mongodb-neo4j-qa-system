from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.mongo_client import mongo_client
from backend.neo4j_client import neo4j_client


settings = get_settings()

app = FastAPI(
    title="MongoDB + Neo4j HotpotQA API",
    description="HotpotQA 多跳问答混合数据库查询接口",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "name": "MongoDB + Neo4j HotpotQA API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health() -> dict:
    neo4j_rows = neo4j_client.run("RETURN 1 AS ok")
    return {
        "ok": neo4j_rows[0]["ok"] == 1 and mongo_client.ping(),
        "mongodb": "connected",
        "neo4j": "connected",
    }


@app.get("/api/search")
def search_questions(
    q: str = Query("", description="关键词"),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    return mongo_client.search(q, limit)


@app.get("/api/question/{question_id}")
def question_detail(question_id: str) -> dict:
    item = mongo_client.get_question(question_id)
    return item or {}


@app.get("/api/question/{question_id}/graph")
def question_graph(question_id: str) -> dict:
    query = """
    MATCH (q:Question {id: $question_id})
    OPTIONAL MATCH (q)-[:HAS_ANSWER]->(a:Answer)
    OPTIONAL MATCH (q)-[:SUPPORTS]->(s:Sentence)<-[:HAS_SENTENCE]-(d:Document)
    RETURN q {
        .id,
        .text,
        .type,
        .level
    } AS question,
    a.text AS answer,
    collect(DISTINCT d {.title}) AS documents,
    collect(DISTINCT s {
        .id,
        .text,
        .sent_id,
        .title
    }) AS sentences
    """
    rows = neo4j_client.run(query, question_id=question_id)
    if not rows:
        mongo_item = mongo_client.get_question(question_id)
        if not mongo_item:
            return {"question": {}, "answer": None, "nodes": [], "links": []}
        question = {
            "id": mongo_item["id"],
            "text": mongo_item["question"],
            "type": mongo_item.get("type"),
            "level": mongo_item.get("level"),
        }
        return {
            "question": question,
            "answer": mongo_item.get("answer"),
            "nodes": [
                {
                    "id": f"q:{question['id']}",
                    "name": question["text"],
                    "category": "Question",
                }
            ],
            "links": [],
        }

    row = rows[0]
    question = row["question"]
    nodes = [
        {
            "id": f"q:{question['id']}",
            "name": question["text"],
            "category": "Question",
        }
    ]
    links = []

    if row.get("answer"):
        nodes.append(
            {
                "id": f"a:{question['id']}",
                "name": row["answer"],
                "category": "Answer",
            }
        )
        links.append(
            {
                "source": f"q:{question['id']}",
                "target": f"a:{question['id']}",
                "name": "HAS_ANSWER",
            }
        )

    for document in row.get("documents", []):
        if not document or not document.get("title"):
            continue
        doc_id = f"d:{document['title']}"
        nodes.append({"id": doc_id, "name": document["title"], "category": "Document"})
        links.append(
            {
                "source": f"q:{question['id']}",
                "target": doc_id,
                "name": "HAS_CONTEXT",
            }
        )

    for sentence in row.get("sentences", []):
        if not sentence or not sentence.get("id"):
            continue
        sent_id = f"s:{sentence['id']}"
        doc_id = f"d:{sentence['title']}"
        nodes.append(
            {
                "id": sent_id,
                "name": sentence["text"],
                "category": "Sentence",
            }
        )
        links.append(
            {
                "source": f"q:{question['id']}",
                "target": sent_id,
                "name": "SUPPORTS",
            }
        )
        links.append(
            {
                "source": doc_id,
                "target": sent_id,
                "name": "HAS_SENTENCE",
            }
        )

    unique_nodes = {node["id"]: node for node in nodes}
    unique_links = {
        (link["source"], link["target"], link["name"]): link for link in links
    }
    return {
        "question": question,
        "answer": row.get("answer"),
        "nodes": list(unique_nodes.values()),
        "links": list(unique_links.values()),
    }


@app.get("/api/clusters/type")
def clusters_by_type() -> list[dict]:
    return mongo_client.cluster_counts("type")


@app.get("/api/clusters/level")
def clusters_by_level() -> list[dict]:
    return mongo_client.cluster_counts("level")


@app.on_event("shutdown")
def shutdown() -> None:
    neo4j_client.close()
    mongo_client.close()
