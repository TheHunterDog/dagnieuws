from pathlib import Path

from chroma_helper import ChromaHelper
from embeddings_model_helper import EmbeddingsModelHelper


class Retriever:
    def __init__(self, embedding_model_name: str, db_path: Path=None):
        self.threshold = 1.7
        self.db_path = db_path
        self.embeddingsModelHelper = EmbeddingsModelHelper(embedding_model_name)

    def retrieve(self, query: str = None, queries: list[str] = None, top_n: int = 8):
        chromaHelper = ChromaHelper(self.embeddingsModelHelper.get_model_name(), db_path=self.db_path)

        chroma = chromaHelper.__load_chroma_client__()
        collection = chroma.get_or_create_collection("articles")
        model = self.embeddingsModelHelper.__load_model__()

        if queries is not None:
            query_embeddings = model.encode(queries).tolist()
        elif query is not None:
            query_embeddings = [model.encode(query).tolist()]
        else:
            raise Exception("No query or queries provided")

        results = collection.query(query_embeddings=query_embeddings, n_results=8)

        best_by_id = {}
        for metadatas, distances in zip(results["metadatas"], results["distances"]):
            for metadata, distance in zip(metadatas, distances):
                print(metadata)
                print(distance)
                if distance > self.threshold:
                    continue
                db_id = metadata["db_id"]
                if db_id not in best_by_id or distance < best_by_id[db_id][0]:
                    best_by_id[db_id] = (distance, metadata)
        ranked = sorted(best_by_id.values(), key=lambda item: item[0])
        return [metadata for _, metadata in ranked[:top_n]]


if __name__ == '__main__':
    retriever = Retriever()
    # print(retriever.retrieve("What is the best way to learn Python?"))
    retriever.retrieve(queries=["Microsoft"])
