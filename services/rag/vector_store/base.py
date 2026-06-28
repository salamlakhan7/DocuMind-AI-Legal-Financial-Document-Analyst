from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    @abstractmethod
    def create_collection(self):
        raise NotImplementedError

    @abstractmethod
    def upsert_embeddings(self, embeddings, chunks):
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, document_id):
        raise NotImplementedError

    @abstractmethod
    def delete_chunk(self, chunk_id):
        raise NotImplementedError

    @abstractmethod
    def query(self, query_vector, top_k=5, filters=None):
        raise NotImplementedError

    @abstractmethod
    def collection_exists(self):
        raise NotImplementedError

    @abstractmethod
    def count(self):
        raise NotImplementedError
