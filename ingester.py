from datetime import datetime
from pathlib import Path
import chromadb.errors
import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chroma_helper import ChromaHelper
from database import Database
from app_logging import Logging
from document import Document
from embeddings_model_helper import EmbeddingsModelHelper
from news_source import NewsSource

CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
ARTICLES_COLLECTION_NAME = "articles"

class Ingester:
    def __init__(self, embedding_model_name: str, db_path: Path = None):
        self.logging = Logging(write_to_file=True, source="Ingester", verbosity=5)
        self.db_path = db_path
        self.embeddingsModelHelper = EmbeddingsModelHelper(embedding_model_name)

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

    def ingest_articles(self, date_from: datetime, date_to: datetime):
        database = Database()
        documents = database.get_documents_filtered_by_dates(date_from, date_to)
        self.__ingest_articles__(documents)



    def __ingest_articles__(self, documents: list[Document]):
        ingested_articles = 0
        articles_skipped = 0

        model = self.embeddingsModelHelper.__load_model__()
        chromaHelper = ChromaHelper(self.embeddingsModelHelper.get_model_name(), db_path=self.db_path)
        chroma = chromaHelper.__load_chroma_client__()
        collection = chroma.get_or_create_collection(ARTICLES_COLLECTION_NAME)

        for document in documents:
            try:
                content = document.full_text if document.full_text else document.description
                if not content or content.strip() == "":
                    articles_skipped+=1
                    continue
                self.logging.info(
                    f"Ingesting article {document.id} from {document.source} with pubdate {document.pub_date}..."
                )
                embedding = model.encode(content)
                database_id = str(document.id)
                source_name = document.get_source_name()
                collection.add(
                    documents=[content],
                    metadatas=[{
                        "source": self.__get_str_or_empty__(source_name),
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
        self.embeddingsModelHelper.__unload_model__()

    def __get_str_or_empty__(self, value):
        return str(value) if value is not None else ""

    def delete_articles(self):
        chromaHelper = ChromaHelper(self.embeddingsModelHelper.embedding_model_name, db_path=self.db_path)
        chroma = chromaHelper.__load_chroma_client__()
        try:
            chroma.delete_collection(ARTICLES_COLLECTION_NAME)
            self.logging.info(f"Deleted collection {ARTICLES_COLLECTION_NAME}")
        except Exception as e:
            self.logging.info(f"Could not delete collection {ARTICLES_COLLECTION_NAME} (might not exist): {e}")
        chromaHelper.__unload_chroma_client__()