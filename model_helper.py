from sentence_transformers import SentenceTransformer


class ModelHelper:
    def __init__(self):
        self.model = None
        self.embedding_model_name = "all-MiniLM-L6-v2"

    def __load_model__(self):
        if self.model is None:
            self.model = SentenceTransformer(
                self.embedding_model_name,
                trust_remote_code=True,
            )
        return self.model

    def __unload_model__(self):
        self.model = None

    def get_model_name(self):
        return self.embedding_model_name