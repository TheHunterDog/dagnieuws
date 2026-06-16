import datetime
import sqlite3
from email.utils import parsedate_to_datetime

from document import Document


class Database:
    def __init__(self):
        self.__create_tables__()
        pass

    def store_document(self, document):
        self.__insert_document_if_not_exists__(document)

    def __connect_database__(self):
        return sqlite3.connect("news.db")

    def __create_tables__(self):
        self.__create_document_table__()

    def __create_document_table__(self):
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        news_source TEXT,
                        title TEXT,
                        description TEXT,
                        link TEXT,
                        guid TEXT,
                        pubdate DATETIME,
                        media_url TEXT,
                        hash TEXT UNIQUE,
                        Created DATETIME DEFAULT CURRENT_TIMESTAMP,
                        summarized_text TEXT,
                        summary TEXT
                        )""")
        conn.commit()
        conn.close()

    def __insert_document_if_not_exists__(self, document: Document):
        if not self.__check_document_exists__(document):
            self.__insert_document__(document)

    def __check_document_exists__(self, document: Document):
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE guid = ? AND news_source = ? OR hash = ?", (document.guid, document.source.name, document.get_unique_hash()))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def __insert_document__(self, document: Document):
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO documents
                              (news_source, title, description, link, guid, pubdate, media_url, hash, summarized_text, summary)
                      VALUES  (?,           ?,     ?,           ?,    ?,    ?,       ?,         ?,    ?,               ?)""", (
                           self.__value_or_none__(document.source.name),
                           self.__value_or_none__(document.title),
                           self.__value_or_none__(document.description),
                           self.__value_or_none__(document.url),
                           self.__value_or_none__(document.guid),
                           self.__normalize_pubdate_to_iso__(document.pub_date),
                           self.__value_or_none__(document.media_url),
                           self.__value_or_none__(document.get_unique_hash()),
                           self.__value_or_none__(document.summarized_text),
                           self.__value_or_none__(document.summary),
                       )
                       )
        conn.commit()
        conn.close()

    def __normalize_pubdate_to_iso__(self, pubdate: str):
        if pubdate is None or pubdate.strip() == "":
            date = datetime.datetime.now()
        else:
            date = parsedate_to_datetime(pubdate)
        return date.isoformat()

    def get_documents(self)->list[Document]:
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY pubdate DESC", )
        documents = cursor.fetchall()
        conn.close()
        return [Document(*document) for document in documents]

    def get_documents_filtered_by_dates(self, start_date: datetime.datetime = None, end_date: datetime.datetime = None)->list[Document]:
        if start_date is None:
        #     start_date set to yesterday
            start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        if end_date is None:
            end_date = datetime.datetime.now()
        if end_date is None:
            end_date = datetime.datetime.now()
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE pubdate BETWEEN ? AND ? ORDER BY pubdate DESC", (start_date.isoformat(), end_date.isoformat()))
        documents = cursor.fetchall()
        conn.close()
        return [Document(*document) for document in documents]

    def get_document_by_id(self, id: int)->Document:
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        document = cursor.fetchone()
        conn.close()
        return Document(*document)

    def __value_or_none__(self, value: str):
        return value if value != None and value.strip() != "" else None
