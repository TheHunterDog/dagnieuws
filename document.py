import hashlib
import json
import re
from typing import List

from bs4 import BeautifulSoup

from news_source import NewsSource
from summarizer import Summarizer

_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
class Document:
    def __init__(self, id=None, source=None, title=None, description=None, url=None, guid=None, pub_date=None, media_url=None, hash=None, created=None, summary=None, summarized_text=None):
        self.title:str = title
        self.description: str = description
        self.url: str = url
        self.pub_date: str = pub_date
        self.guid: str = guid
        self.media_url: str = media_url
        self.source: NewsSource = source
        self.id: str = id
        self.hash: str = hash
        self.created: str = created
        self.summarized_text: str = summarized_text # This is always created by us
        self.summary: str = summary # This is always created by the publisher


    def convert_from_document(self, document_item):
        soup = BeautifulSoup(document_item, 'html.parser')
        self.__extract_item__(soup, "title")
        self.__extract_item__(soup, "description", alternative_naming=["content"])
        self.__extract_item__(soup, "link", bind_to="url")
        self.__extract_item__(soup, "guid")
        self.__extract_item__(soup, "pubDate", "pub_date", ["pubdate"])
        self.__extract_item__(soup, "media_url", alternative_naming=["enclosure"])
        self.__extract_item__(soup, "source")
        self.__extract_item__(soup, "summary")
        print(self.title)
        print(self.pub_date)
        return self


    def summarize(self):
        # Some articles are already summarized by the publisher
        if self.summary:
            return self.summary
        print("Summarizing...")
        summarizer = Summarizer()
        self.summarized_text = summarizer.summarize_using_ollama(self.description)

    def convert_news_to_document(self, news, news_source: NewsSource = None):
        soup = BeautifulSoup(news, 'html.parser')
        possible_items_namings = ["item", "entry"]
        items = soup.find_all(possible_items_namings)
        documents = []
        for item in items:
            item = str(item)
            document = Document()
            document.convert_from_document(item)
            document.source = news_source
            documents.append(document)
        return documents

    def __extract_item__(self, soup: BeautifulSoup, item_name: str, bind_to: str = None, alternative_naming:List[str] = None):
        item = soup.find(item_name)
        str_item = str(item)
        if item:
            if item.contents:
                # Tag wraps its own content, e.g. <title>Some text</title>
                value = item.get_text().strip()
            else:
                # Void/self-closing tag, e.g. <link/>nos.nl/1289317hsdafl
                # the real value is the next node in document order
                next_node = item.next_element
                value = next_node.get_text().strip() if hasattr(next_node, "get_text") else str(next_node).strip()
            self.__setattr__(bind_to if bind_to is not None else item_name, self.__clean_text__(value))
        else:
            if alternative_naming is not None and len(alternative_naming) > 0:
                print(f"Could not find {item_name}")
                self.__extract_item__(soup, alternative_naming[0], bind_to if bind_to is not None else item_name, alternative_naming[1:])
        return self

    def __clean_text__(self, value: str) -> str:
        if not value:
            return ""
        # In case the parser left the CDATA wrapper in as literal text
        value = _CDATA_RE.sub(r"\1", value)
        # Strip any embedded HTML tags, unescapes entities as a side effect
        value = BeautifulSoup(value, "html.parser").get_text()
        return value.strip()

    def get_unique_hash(self) -> str:
        payload = json.dumps(
            [
                self.title,
                self.description,
                self.url,
                self.pub_date,
                self.guid,
                self.media_url,
                str(self.source),
            ],
            ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()