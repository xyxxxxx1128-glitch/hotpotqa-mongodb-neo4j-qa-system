import hashlib
from collections.abc import Iterable
from typing import Any

from neo4j import GraphDatabase

from backend.config import get_settings


def sentence_key(title: str, sent_id: int, text: str) -> str:
    raw = f"{title}|{sent_id}|{text}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


class HotpotQANeo4jImporter:
    def __init__(self) -> None:
        settings = get_settings()
        self.database = settings.neo4j_database
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def close(self) -> None:
        self.driver.close()

    def create_constraints(self) -> None:
        statements = [
            "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
            "CREATE CONSTRAINT answer_text IF NOT EXISTS FOR (a:Answer) REQUIRE a.text IS UNIQUE",
            "CREATE CONSTRAINT document_title IF NOT EXISTS FOR (d:Document) REQUIRE d.title IS UNIQUE",
            "CREATE CONSTRAINT sentence_id IF NOT EXISTS FOR (s:Sentence) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT type_name IF NOT EXISTS FOR (t:Type) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT level_name IF NOT EXISTS FOR (l:Level) REQUIRE l.name IS UNIQUE",
        ]
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                session.run(statement)

    def clear_database(self) -> None:
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")

    def import_items(
        self,
        items: Iterable[dict[str, Any]],
        progress_every: int = 1000,
        include_all_context_sentences: bool = False,
    ) -> int:
        count = 0
        with self.driver.session(database=self.database) as session:
            for item in items:
                session.execute_write(
                    self._import_one,
                    item,
                    include_all_context_sentences,
                )
                count += 1
                if progress_every > 0 and count % progress_every == 0:
                    print(f"Imported {count} records...")
        return count

    @staticmethod
    def _import_one(
        tx: Any,
        item: dict[str, Any],
        include_all_context_sentences: bool,
    ) -> None:
        question_id = str(item["id"])
        question_text = item["question"]
        answer_text = item.get("answer", "")
        question_type = item.get("type", "unknown")
        level = item.get("level", "unknown")
        context = normalize_context(item.get("context", []))
        supporting_facts = normalize_supporting_facts(item.get("supporting_facts", []))

        tx.run(
            """
            MERGE (q:Question {id: $id})
            SET q.text = $text,
                q.type = $type,
                q.level = $level
            MERGE (a:Answer {text: $answer})
            MERGE (q)-[:HAS_ANSWER]->(a)
            MERGE (t:Type {name: $type})
            MERGE (q)-[:HAS_TYPE]->(t)
            MERGE (l:Level {name: $level})
            MERGE (q)-[:HAS_LEVEL]->(l)
            """,
            id=question_id,
            text=question_text,
            answer=answer_text,
            type=question_type,
            level=level,
        )

        support_set = {(fact["title"], int(fact["sent_id"])) for fact in supporting_facts}

        for doc in context:
            title = doc["title"]
            tx.run(
                """
                MATCH (q:Question {id: $question_id})
                MERGE (d:Document {title: $title})
                MERGE (q)-[:HAS_CONTEXT]->(d)
                """,
                question_id=question_id,
                title=title,
            )
            for sent_id, sentence in enumerate(doc["sentences"]):
                is_support = (title, sent_id) in support_set
                if not include_all_context_sentences and not is_support:
                    continue

                sid = sentence_key(title, sent_id, sentence)
                tx.run(
                    """
                    MATCH (q:Question {id: $question_id})
                    MATCH (d:Document {title: $title})
                    MERGE (s:Sentence {id: $sentence_id})
                    SET s.text = $text,
                        s.sent_id = $sent_id,
                        s.title = $title
                    MERGE (d)-[:HAS_SENTENCE]->(s)
                    """,
                    question_id=question_id,
                    title=title,
                    sentence_id=sid,
                    text=sentence,
                    sent_id=sent_id,
                )
                if is_support:
                    tx.run(
                        """
                        MATCH (q:Question {id: $question_id})
                        MATCH (s:Sentence {id: $sentence_id})
                        MERGE (q)-[:SUPPORTS]->(s)
                        """,
                        question_id=question_id,
                        sentence_id=sid,
                    )


def normalize_context(context: Any) -> list[dict[str, Any]]:
    if isinstance(context, dict):
        titles = context.get("title", [])
        sentences = context.get("sentences", [])
        return [
            {"title": title, "sentences": sentence_list}
            for title, sentence_list in zip(titles, sentences)
        ]
    return context


def normalize_supporting_facts(facts: Any) -> list[dict[str, Any]]:
    if isinstance(facts, dict):
        titles = facts.get("title", [])
        sent_ids = facts.get("sent_id", [])
        return [
            {"title": title, "sent_id": sent_id}
            for title, sent_id in zip(titles, sent_ids)
        ]
    return facts
