import datetime
from email.utils import parsedate_to_datetime
import rss_sources as sources
from database import Database
from document import Document
from app_logging import Logging

class Fetcher:
    def __init__(self):
        self.logging = Logging(True, "Fetcher")
        self.db = Database()

    def fetch(self, target_date_str=None):
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            except ValueError:
                self.logging.error(f"Invalid date format: {target_date_str}")

        total_found = 0
        total_ingested = 0
        total_failed = 0

        for source in sources.newsSources:
            self.logging.info(f"Processing feed: {source.name} ({source.url})")
            try:
                news = source.get_news()
                documents = Document().convert_news_to_document(news, news_source=source)
                for document in documents:
                    # Date filtering
                    if target_date:
                        try:
                            # Use parsedate_to_datetime for robust RSS date parsing
                            pub_dt = parsedate_to_datetime(document.pub_date)
                            if pub_dt.date() != target_date:
                                continue
                        except Exception:
                            # Skip if date is missing or unparseable when target_date is set
                            continue

                    total_found += 1
                    if self.db.__check_document_exists__(document):
                        self.logging.info(
                            f"Document {document.id} already exists in database. Skipping..."
                        )
                        continue
                    # Task 1: Fetch and extract full text
                    document.fetch_full_text()

                    self.db.store_document(document)
                    total_ingested += 1
            except Exception as e:
                self.logging.error(f"Failed to process feed {source.name}: {e}")
                total_failed += 1
                continue

        print(f"Total articles found for {target_date_str if target_date_str else 'all dates'}: {total_found}")
        print(f"Ingested (full text ok): {total_ingested}")
        print(f"Total failed feeds: {total_failed}")
