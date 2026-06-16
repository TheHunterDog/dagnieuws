from pathlib import Path

import chromadb


class ChromaHelper:
    def __init__(self, embedding_model_name: str = "BAAI/bge-m3"):
        self.chromaClient = None
        base_dir = Path(__file__).resolve().parent
        self.db_path = (base_dir / "dbs" / embedding_model_name / "chroma_db").resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def __load_chroma_client__(self):
        if self.chromaClient is None:
            self.chromaClient = chromadb.PersistentClient(path=str(self.db_path))
        return self.chromaClient

    def __unload_chroma_client__(self):
        self.chromaClient = None