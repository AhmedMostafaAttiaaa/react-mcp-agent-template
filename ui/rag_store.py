"""Disk-backed RAG stores. Both are CPU-friendly and need no external server:
Chroma runs in local persistent mode (SQLite + Parquet on disk), and the graph
store is a networkx graph pickled to disk.
"""
import pickle
from pathlib import Path

import chromadb
import networkx as nx


class VectorStore:
    def __init__(self, persist_dir: str, collection_name: str = "documents"):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, ids: list, embeddings: list, documents: list, metadatas: list) -> None:
        # upsert so re-ingesting the same file/chunk just overwrites instead of erroring
        self.collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def query(self, query_embedding: list, n_results: int = 5) -> list:
        result = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        hits = []
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for doc, meta, distance in zip(docs, metas, distances):
            hits.append({"text": doc, "metadata": meta, "distance": distance})
        return hits

    def is_empty(self) -> bool:
        return self.collection.count() == 0


class GraphStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.graph = nx.MultiDiGraph()
        if self.path.exists():
            self.load()

    def add_triple(self, subject: str, relation: str, obj: str, source: str) -> None:
        self.graph.add_node(subject)
        self.graph.add_node(obj)
        self.graph.add_edge(subject, obj, relation=relation, source=source)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump(self.graph, f)

    def load(self) -> None:
        with open(self.path, "rb") as f:
            self.graph = pickle.load(f)

    def is_empty(self) -> bool:
        return self.graph.number_of_nodes() == 0

    def query(self, entity: str, hops: int = 1) -> list:
        if entity not in self.graph:
            matches = [n for n in self.graph.nodes if entity.lower() in str(n).lower()]
            if not matches:
                return []
            entity = matches[0]

        facts = []
        seen_edges = set()
        frontier = {entity}
        for _ in range(max(hops, 1)):
            next_frontier = set()
            for node in frontier:
                for _, target, data in self.graph.out_edges(node, data=True):
                    key = (node, data.get("relation"), target)
                    if key not in seen_edges:
                        seen_edges.add(key)
                        facts.append({"subject": node, "relation": data.get("relation"), "object": target, "source": data.get("source")})
                    next_frontier.add(target)
                for source, _, data in self.graph.in_edges(node, data=True):
                    key = (source, data.get("relation"), node)
                    if key not in seen_edges:
                        seen_edges.add(key)
                        facts.append({"subject": source, "relation": data.get("relation"), "object": node, "source": data.get("source")})
                    next_frontier.add(source)
            frontier = next_frontier
        return facts
