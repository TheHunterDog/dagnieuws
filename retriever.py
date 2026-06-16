from chroma_helper import ChromaHelper
from model_helper import ModelHelper


class Retriever:
    def __init__(self):
        pass

    def retrieve(self, query: str = None, queries: list[str] = None):
        modelHelper = ModelHelper()
        chromaHelper = ChromaHelper(modelHelper.get_model_name())

        chroma = chromaHelper.__load_chroma_client__()
        collection = chroma.get_or_create_collection("articles")
        model = modelHelper.__load_model__()

        if queries is not None:
            query_embedding = model.encode(queries)
        elif query is not None:
            query_embedding = model.encode(query).tolist()
        else:
            raise Exception("No query or queries provided")
        results = collection.query(query_embeddings=query_embedding, n_results=5)

        return results