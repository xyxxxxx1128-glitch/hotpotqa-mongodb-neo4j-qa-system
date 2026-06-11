from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    question: str
    answer: str | None = None
    type: str | None = None
    level: str | None = None


class GraphNode(BaseModel):
    id: str
    name: str
    category: str


class GraphLink(BaseModel):
    source: str
    target: str
    name: str


class GraphResponse(BaseModel):
    question: dict
    answer: str | None = None
    nodes: list[GraphNode]
    links: list[GraphLink]


class ClusterItem(BaseModel):
    name: str
    count: int
