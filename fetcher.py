import rss_sources as sources
from database import Database
from document import Document
from app_logging import Logging
class Fetcher:
    def __init__(self):
        pass
    def fetch(self):
        logging = Logging(True, "Ingest")
        error_domains = []
        database = Database()
        for source in sources.newsSources:
            try:
                news = source.get_news()
                logging.info(source.name)
                documents = Document().convert_news_to_document(news, news_source = source)
                for document in documents:
                    database.store_document(document)
            except Exception as e:
                error_domains.append((source,e))
                logging.error(f"in domain {source}: {e}")


        logging.info("errored domains:")
        for domain in error_domains:
            logging.info(domain[0].name)
            logging.error(domain[1])
