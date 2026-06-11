import json
from pathlib import Path

from backend.neo4j_client import neo4j_client


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "frontend" / "sample-data.js"


def main() -> None:
    questions = neo4j_client.run(
        """
        MATCH (q:Question)
        OPTIONAL MATCH (q)-[:HAS_ANSWER]->(a:Answer)
        RETURN q.id AS id,
               q.text AS question,
               a.text AS answer,
               q.type AS type,
               q.level AS level
        ORDER BY q.id
        LIMIT 30
        """
    )
    graphs = {}
    for question in questions:
        graph = build_graph(question["id"])
        graphs[question["id"]] = graph

    clusters = {
        "type": neo4j_client.run(
            """
            MATCH (q:Question)
            RETURN coalesce(q.type, "unknown") AS name, count(q) AS count
            ORDER BY count DESC
            """
        ),
        "level": neo4j_client.run(
            """
            MATCH (q:Question)
            RETURN coalesce(q.level, "unknown") AS name, count(q) AS count
            ORDER BY count DESC
            """
        ),
    }

    payload = {"questions": questions, "graphs": graphs, "clusters": clusters}
    text = "window.SAMPLE_DATA = "
    text += json.dumps(payload, ensure_ascii=False, indent=2)
    text += ";\n"
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    print(f"Exported static frontend data to {OUTPUT_FILE}")


def build_graph(question_id: str) -> dict:
    rows = neo4j_client.run(
        """
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
        """,
        question_id=question_id,
    )
    if not rows:
        return {"question": {}, "answer": None, "nodes": [], "links": []}

    row = rows[0]
    question = row["question"]
    qid = f"q:{question['id']}"
    nodes = [{"id": qid, "name": question["text"], "category": "Question"}]
    links = []

    if row.get("answer"):
        aid = f"a:{question['id']}"
        nodes.append({"id": aid, "name": row["answer"], "category": "Answer"})
        links.append({"source": qid, "target": aid, "name": "HAS_ANSWER"})

    for document in row.get("documents", []):
        if not document or not document.get("title"):
            continue
        did = f"d:{document['title']}"
        nodes.append({"id": did, "name": document["title"], "category": "Document"})
        links.append({"source": qid, "target": did, "name": "HAS_CONTEXT"})

    for sentence in row.get("sentences", []):
        if not sentence or not sentence.get("id"):
            continue
        sid = f"s:{sentence['id']}"
        did = f"d:{sentence['title']}"
        nodes.append({"id": sid, "name": sentence["text"], "category": "Sentence"})
        links.append({"source": qid, "target": sid, "name": "SUPPORTS"})
        links.append({"source": did, "target": sid, "name": "HAS_SENTENCE"})

    unique_nodes = {node["id"]: node for node in nodes}
    unique_links = {(link["source"], link["target"], link["name"]): link for link in links}
    return {
        "question": question,
        "answer": row.get("answer"),
        "nodes": list(unique_nodes.values()),
        "links": list(unique_links.values()),
    }


if __name__ == "__main__":
    main()
