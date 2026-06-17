from database import Database
from summarizer import Summarizer

db = Database()

selected_docs = db.get_documents()[:3]

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
