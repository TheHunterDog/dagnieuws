# pipeline
import datetime
import os
import yaml
import json
from zoneinfo import ZoneInfo

from clustering import Clustering
from database import Database
from fetcher import Fetcher
from ingester import Ingester
from retriever import Retriever
from summarizer import Summarizer

def run_pipeline(date_str=None):
    embeddings_model_name = "BAAI/bge-m3"

    # Stage 1: Resolve target date
    tz = ZoneInfo("Europe/Amsterdam")
    if date_str:
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
            return
    else:
        target_date = (datetime.datetime.now(tz) - datetime.timedelta(days=1)).date()
    
    date_iso = target_date.isoformat()
    print(f"--- Starting Pipeline for {date_iso} ---")
    start_time = datetime.datetime.now()

    # Stage 2: FETCH
    print(f"[1/6] Fetching RSS feeds for {date_iso}...")
    fetcher = Fetcher()
    fetcher.fetch(date_iso)

    # Stage 3: CLUSTER
    print(f"[2/6] Clustering articles into story groups...")
    clusterer = Clustering(embedding_model_name=embeddings_model_name)
    clusterer.cluster_documents()

    # Stage 4: INGEST (Populate ChromaDB)
    print(f"[3/6] Ingesting articles into vector store...")
    ingester = Ingester(embeddings_model_name)
    # Remove current embeddings database that have old data
    ingester.delete_articles()

    # Calculate date range for the target date
    date_from = datetime.datetime.combine(target_date, datetime.time.min).replace(tzinfo=tz)
    date_to = datetime.datetime.combine(target_date, datetime.time.max).replace(tzinfo=tz)

    ingester.ingest_articles(date_from, date_to)

    # Stage 5: RANK
    print(f"[4/6] Ranking clusters against profile topics...")
    if not os.path.exists("profile.yaml"):
        print("profile.yaml not found. Using default queries.")
        all_queries = ["AI", "Machine Learning", "technology", "artificial intelligence", "Quantum", "Breaking news", "Future"]
    else:
        with open("profile.yaml", "r") as f:
            profile = yaml.safe_load(f)
        
        all_queries = []
        for topic in profile.get('topics', []):
            all_queries.extend(topic.get('phrasings', []))
    
    retriever = Retriever(embeddings_model_name)
    # Retrieve top articles based on profile queries
    results = retriever.retrieve(queries=all_queries, top_n=15)
    
    db = Database()
    selected_docs = []
    seen_urls = set()
    for item in results:
        doc = db.get_document_by_id(item['db_id'])
        if doc and doc.url not in seen_urls:
            selected_docs.append(doc)
            seen_urls.add(doc.url)

    # Stage 6: SUMMARIZE
    print(f"[5/6] Generating Dutch summaries...")
    summarizer = Summarizer()
    for doc in selected_docs:
        if doc.summarized_text is not None:
            continue
        print(f"  Summarizing: {doc.title}")
        # Use full_text if available, otherwise description
        text_to_summarize = doc.full_text if doc.full_text else doc.description
        if text_to_summarize:
            try:
                doc.summarized_text = summarizer.summarize_with_relevance(text_to_summarize)
                db.__update_document__(doc)
            except Exception as e:
                print(f"  Failed to summarize {doc.id}: {e}")
                doc.summarized_text = doc.description[:200] + "..."

    # Stage 7: ASSEMBLE
    # Content hygiene policy: digest emits summaries + links only.
    # Never republish full article text. Enforced by never writing doc.full_text
    # and capping description excerpts at 300 chars.
    print(f"[6/6] Assembling digest...")
    os.makedirs("daily_digest", exist_ok=True)
    digest_path = f"daily_digest/{date_iso}.md"
    with open(digest_path, "w", encoding="utf-8") as f:
        # Write astro header
        f.write(f"""
---
title: 'Dagkrant — {date_iso}'
description: 'Wat er is gebeurd op {date_iso} in Nederland en over de wereld.'
pubDate: '{target_date}'
---

""")
        if not selected_docs:
            f.write("Geen relevant nieuws gevonden voor deze dag.\n")
        else:
            for doc in selected_docs:
                # Hygiene: only write summarized_text (not full_text)
                body = doc.summarized_text
                if not body:
                    body = (doc.description or "")[:300]
                f.write(f"### {doc.title}\n")
                f.write(f"**Bron:** {doc.source.name if hasattr(doc.source, 'name') else str(doc.source)} | **Datum:** {doc.pub_date}\n\n")
                f.write(f"{body}\n\n")
                f.write(f"[Lees meer]({doc.url})\n\n---\n\n")
        
        # Footer stats
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        f.write(f"\n*Gegenereerd op {datetime.datetime.now().isoformat()} in {duration.total_seconds():.1f}s*")

    print(f"Digest created: {digest_path}")

    # Stage 8: LOG
    os.makedirs("ops", exist_ok=True)
    with open("ops/run_log.jsonl", "a") as log_file:
        log_entry = {
            "date": date_iso,
            "timestamp": datetime.datetime.now().isoformat(),
            "duration_s": duration.total_seconds(),
            "articles_selected": len(selected_docs)
        }
        log_file.write(json.dumps(log_entry) + "\n")

    # Performance delta for database
    db.store_performance_delta(duration)
    print("Performance entry has been made")

    return digest_path, target_date

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    args = parser.parse_args()
    run_pipeline(args.date)
