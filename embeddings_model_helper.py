import torch
from sentence_transformers import SentenceTransformer

from app_logging import Logging


class EmbeddingsModelHelper:
    logging = Logging(True, "ModelHelper")

    def __init__(self, embedding_model_name: str):
        self.model = None
        self.embedding_model_name = embedding_model_name

    def __load_model__(self):
        if self.model is None:
            self.model = SentenceTransformer(
                self.embedding_model_name,
                trust_remote_code=True,
                device=self.__select_best_torch_device__(),
            )
        return self.model

    def __unload_model__(self):
        self.model = None

    def get_model_name(self):
        return self.embedding_model_name

    def __select_best_torch_device__(self):
        self.logging.info("Selecting best torch device...")
        if torch.cuda.is_available():
            self.logging.info("CUDA is available, using it.")
            return "cuda"
        elif torch.backends.mps.is_available():
            self.logging.info("MPS is available, using it.")
            return "mps"
        else:
            self.logging.info("CUDA and MPS are not available, using CPU.")
            return "cpu"