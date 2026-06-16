from pathlib import Path

import chromadb.errors
import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chroma_helper import ChromaHelper
from database import Database
from app_logging import Logging
from model_helper import ModelHelper

CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

class Ingester:
    def __init__(self):
        self.logging = Logging(write_to_file=True, source="Ingester", verbosity=5)
        self.embedding_model_name = EMBEDDING_MODEL_NAME

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n# ",  # h1
                "\n## ",  # h2
                "\n### ",  # h3
                "\n#### ",  # h4
                "\n##### ",  # h5
                "\n###### ",  # h6
                "\n\n",  # paragraphs
                "\n",  # line breaks
                ". ",  # sentences
                ", ",  # clauses
                " "  # words
            ]
        )

        self.model = None

    def __select_best_torch_device__(self):
        self.logging.info("Selecting best torch device...")
        if torch.cuda.is_available():
            self.logging.info("CUDA is available, using it.")
            return "cuda"
        elif torch.backends.mps.is_available():
            self.logging.info("MPS is available, using it.")
            return "mps"
        else:
            self.logging.info("CUDA and MPS are not available, using CPU.")
            return "cpu"

    def ingest_articles(self):
        ingested_articles = 0
        articles_skipped = 0
        # assuming the responses folder

        database = Database()
        documents = database.get_documents_filtered_by_dates()
        modelHelper = ModelHelper()
        model = modelHelper.__load_model__()
        chromaHelper = ChromaHelper(modelHelper.get_model_name())
        chroma = chromaHelper.__load_chroma_client__()
        collection = chroma.get_or_create_collection("articles")

        for document in documents:
            try:
                if(document.description is None or document.description.strip() == ""):
                    articles_skipped+=1
                    continue
                self.logging.info(
                    f"Ingesting article {document.id} from {document.source} with pubdate {document.pub_date}..."
                )
                embedding = model.encode(document.description)
                database_id = str(document.id)
                collection.add(
                    documents=[document.description],
                    metadatas=[{
                        "source": self.__get_str_or_empty__(document.source) if type(document.source) == str else document.source.name,
                        "pubdate": self.__get_str_or_empty__(document.pub_date),
                        "url": self.__get_str_or_empty__(document.url),
                        "guid": self.__get_str_or_empty__(document.guid),
                        "db_id": self.__get_str_or_empty__(database_id)
                    }],
                    ids=[database_id],
                    embeddings=[embedding],
                )
            except Exception as e:
                articles_skipped += 1
                self.logging.error(f"Error ingesting article {document.id}: {e}")
                continue

            ingested_articles += 1

        print(f"Ingested {ingested_articles} articles, skipped {articles_skipped} articles")

        chromaHelper.__unload_chroma_client__()
        modelHelper.__unload_model__()
    def __get_str_or_empty__(self, value):
        return str(value) if value is not None else ""

    def delete_articles(self):
        chromaHelper = ChromaHelper(self.embedding_model_name)
        chroma = chromaHelper.__load_chroma_client__()
        try:
            if not chroma.get_collection("articles"):
                return
        except chromadb.errors.NotFoundError:
            return
        chroma.delete_collection("articles")
        chromaHelper.__unload_chroma_client__()