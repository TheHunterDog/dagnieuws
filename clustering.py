import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import normalize

from database import Database
from embeddings_model_helper import EmbeddingsModelHelper


class Clustering:
    def __init__(self, embedding_model_name: str):
        self.embedding_model_name = embedding_model_name

    def cluster_documents(self):
        database = Database()
        documents = database.get_documents()

        if documents is None or len(documents) == 0:
            return []

        embeddings = []
        article_ids = []

        modelhelper = EmbeddingsModelHelper(embedding_model_name=self.embedding_model_name)
        model = modelhelper.__load_model__()

        for document in documents:
            content = document.full_text if document.full_text else document.description
            if not content or content.strip() == "":
                continue
            combined_text = f"{document.title}. {content[:500]}"

            article_ids.append(document.id)
            embeddings.append(model.encode(combined_text))


        embeddings_matrix = np.array(embeddings)
        normalized_embeddings = normalize(embeddings_matrix)

        distance_threshold = 0.22
        model_cluster = AgglomerativeClustering(
            n_clusters=None,
            metric='cosine',
            linkage='average',
            distance_threshold=distance_threshold
        )

        cluster_labels = model_cluster.fit_predict(normalized_embeddings)

        for i, article_id in enumerate(article_ids):
            self.__update_cluster_id_in_database__(int(cluster_labels[i]), article_id)


    def __update_cluster_id_in_database__(self, cluster_id: int, document_id: str):
        database = Database()
        database.add_cluster_id(document_id, cluster_id)


