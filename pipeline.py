# pipeline
import datetime

from database import Database
from fetcher import Fetcher
from ingester import Ingester
from retriever import Retriever
from summarizer import Summarizer

# get start time
start = datetime.datetime.now()

# Fetch latest data
fetcher = Fetcher()
fetcher.fetch()

# Remove current embeddings database that have old data
ingester = Ingester()
ingester.delete_articles()
ingester.ingest_articles()

# Retrieve intressting articles based on keywords
retriever = Retriever()
articles = retriever.retrieve(queries=["AI", "Machine Learning", "technology", "artificial intelligence", "Quantum", "Breaking news", "Future"])

# Get full article text
database = Database()
documents = [database.get_document_by_id(id) for id in articles['ids'][0]]
# remove duplicate documents based on id
seen_document_ids = set()
documents = [
    document
    for document in documents
    if document.id not in seen_document_ids and not seen_document_ids.add(document.id)
]

for document in documents:
    document.summarize()

# Write to daily digest file
curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
# create daily digest folder
import os
os.makedirs("daily_digest", exist_ok=True)

with open(f"daily_digest/{curr_date}.md", "w") as file:
    for article in documents:
        file.write(f"[{article.source}]{article.summarized_text}  [LINK]({article.url}) \n\n")

end = datetime.datetime.now()
delta = end - start
print("pipeline took: ", delta.total_seconds())

database.store_performance_delta(delta)
print("Entry has been made")