import datetime
import sqlite3
import os
from email.utils import parsedate_to_datetime

from sympy import false

from document import Document


class Database:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.__create_tables__()
        pass

    def __connect_performance_database__(self):
        return sqlite3.connect(os.path.join(self.base_dir, "performance.db"))

    def store_performance_delta(self, delta: datetime.timedelta):
        self.__create_performance_table__()
        conn = self.__connect_performance_database__()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO performance
                       (delta) VALUES (?)""", (str(delta),)
        )
        conn.commit()
        conn.close()

    def __create_performance_table__(self):
        conn = self.__connect_performance_database__()
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delta TEXT,
            Created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
    def store_document(self, document):
        self.__insert_document__(document)

    def __connect_database__(self):
        return sqlite3.connect(os.path.join(self.base_dir, "news.db"))

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
                        summary TEXT,
                        cluster_id INTEGER,
                        full_text TEXT,
                        fetch_status TEXT
                        )""")
        conn.commit()
        conn.close()

    def __insert_document_if_not_exists__(self, document: Document):
        if not self.__check_document_exists__(document):
            self.__insert_document__(document)

    def __check_document_exists__(self, document: Document):
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM documents WHERE id = ? OR guid = ? or (title = ? and pubdate = ? and news_source = ?)", (document.id, document.guid, document.title, document.pub_date, document.get_source_name()))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def __insert_document__(self, document: Document):
        if self.__check_document_exists__(document):
            return
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO documents
                              (news_source, title, description, link, guid, pubdate, media_url, hash, summarized_text, summary, full_text, fetch_status)
                      VALUES  (?,           ?,     ?,           ?,    ?,    ?,       ?,         ?,    ?,               ?,       ?,         ?)""", (
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
                           self.__value_or_none__(document.full_text),
                           self.__value_or_none__(document.fetch_status),
                       )
                       )
        conn.commit()
        conn.close()

    def __update_document__(self, document: Document):
        if not self.__check_document_exists__(document):
            return
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("""UPDATE documents SET 
                                               title = ?, 
                                               description = ?, 
                                               link = ?, 
                                               guid = ?, 
                                               media_url = ?,
                                               hash = ?, 
                                               summarized_text = ?, 
                                               summary = ?, 
                                               full_text = ?, 
                                               fetch_status = ? 
                          WHERE id = ?""", (
            self.__value_or_none__(document.title),
            self.__value_or_none__(document.description),
            self.__value_or_none__(document.url),
            self.__value_or_none__(document.guid),
            self.__value_or_none__(document.media_url),
            self.__value_or_none__(document.get_unique_hash()),
            self.__value_or_none__(document.summarized_text),
            self.__value_or_none__(document.summary),
            self.__value_or_none__(document.full_text),
            self.__value_or_none__(document.fetch_status),
            document.id

        ))
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

    def get_documents_filtered_by_dates(self, start_date: datetime.datetime, end_date: datetime.datetime)->list[Document]:
        if start_date is None:
        #     start_date set to yesterday
            start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        if end_date is None:
            end_date = datetime.datetime.now()
        conn = self.__connect_database__()
        cursor = conn.cursor()
        query = """
        SELECT * FROM documents 
        WHERE id IN (
            SELECT id FROM (
                SELECT id, MAX(LENGTH(description)) 
                FROM documents 
                WHERE pubdate BETWEEN ? AND ?
                GROUP BY cluster_id
            )
        )
        ORDER BY pubdate DESC;
        """
        cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
        documents = cursor.fetchall()
        conn.close()
        return [Document(*document) for document in documents]

    def get_document_by_id(self, id: str)-> Document | None:
        conn = self.__connect_database__()
        cursor = conn.cursor()
        print("Fetching document with id:", id)
        cursor.execute("SELECT * FROM documents WHERE id = ?", (id,))
        document = cursor.fetchone()
        conn.close()
        if document is None:
            print("Document not found")
            return None
        return Document(*document)

    def __value_or_none__(self, value: str):
        return value if value != None and value.strip() != "" else None

    def add_cluster_id(self, document_id: str, cluster_id: int):
        conn = self.__connect_database__()
        cursor = conn.cursor()
        cursor.execute("UPDATE documents SET cluster_id = ? WHERE id = ?", (cluster_id, document_id))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    database = Database()
    documents = database.get_documents_filtered_by_dates()
    for document in documents:
        print(document.title)