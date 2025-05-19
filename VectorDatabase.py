import chromadb
from chromadb.utils import embedding_functions
from chromadb.api import ClientAPI
from chromadb.api.types import (
    Documents,
    EmbeddingFunction,
)
from chromadb.api.models.Collection import Collection

#################################################################
# This is a Facade over the Vector Database used                #
#################################################################
class VectorDatabase:
    def __init__(
            self,
            path: str = "./chromadb",
    ):
        self.client = chromadb.PersistentClient(path=path)

    def getClient(
            self,
        ) -> ClientAPI:
        return self.client

    def getOpenAIEmbeddings(
            self,
            model_name: str="text-embedding-ada-002",
            api_key: str=""
    ) -> EmbeddingFunction[Documents]:
        return embedding_functions.OpenAIEmbeddingFunction(
                    model_name=model_name,
                    api_key=api_key
        )

    def getHuggingFaceEmbeddings(
            self,
            model_name: str="sentence-transformers/all-MiniLM-L6-v2",
            api_key: str=""
    ) -> EmbeddingFunction[Documents]:
        return embedding_functions.HuggingFaceEmbeddingFunction(
            model_name=model_name,
            api_key=api_key
        )

    def getDefaultEmbeddings(
            self
    ) -> EmbeddingFunction[Documents]:
        return embedding_functions.DefaultEmbeddingFunction()

    def getSentenceTransformerEmbeddingFunction(
            self,
            model_name
    ) -> EmbeddingFunction[Documents]:
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name)

    def getCollection(
            self,
            name: str,
            embedding_function: EmbeddingFunction[Documents]=None
    ) -> Collection:
        if not embedding_function:
            embedding_function = self.getDefaultEmbeddings()
        return self.client.get_or_create_collection(name=name, embedding_function=embedding_function)

    def addInCollection(
            self,
            collection: Collection,
            document: str,
            metadata: {},
            id: str
    ):
        collection.add(documents=[document], metadatas=[metadata], ids=[id])

    def addChunksInCollection(
            self,
            collection: Collection,
            chunks: [],
            metadata: {},
            id: str
    ):
        i = 1
        for chunk in chunks:
            chunk_id = id+"_"+i
            self.addInCollection(collection=collection, document=chunk, metadata=metadata, id=chunk_id)

    def query(
            self,
            collection: Collection,
            query_texts: [],
            where: {}={},
            n_results: int=10
    ) -> []:
        result = collection.query(query_texts=query_texts, where=where, n_results=n_results)
        books = []
        i = 0
        for id in result['ids'][0]:
            books.append({
                "content": result['documents'][0][i],
                "id": id,
                "title": result['metadatas'][0][i]['title'],
                "author": result['metadatas'][0][i]['author'],
                "url": result['metadatas'][0][i]['url'],
                "distance": result['distances'][0][i]
            })
            i += 1
        return books
