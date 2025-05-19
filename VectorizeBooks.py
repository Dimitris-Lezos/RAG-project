from VectorDatabase import VectorDatabase
import json
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter

##################################################################################
# This code:
# - Reads the Scrapped data
# - Cuts it in chunks
# - Vectorizes it and Stores in Database
#
# A number of different Chunks have been tried
# A number of different Vectorizations have been tried
##################################################################################

def storeBooksInCollection(books, collection, chunk_size=None, chunk_overlap=None):
    iBook = 0
    for book in books:
        iBook += 1
        title = book['title']
        author = book['author']['name']
        content = book['description']
        url = book['url']
        id = np.char.rpartition(book["url"], '/')[2] + "_"
        # Bug: ChromaDB does not support arrays in metadata :-/
        genre = ""
        try:
            genre = book['genres'][0]
        except:
            genre = str(book['genres'])
        metadata = {
            "title": title,
            "genre": genre,
            "author": author,
            "url": url
        }
        i = 0
        if chunk_size:
            # Append all available content for this book
            for review in book['reviews']:
                content = content + " " + review['content']
            # Split the content in chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            print("\nChunking", title, iBook, "/", len(books), end="")
            chunks = text_splitter.create_documents([content])
            for chunk in chunks:
                try:
                    if len(collection.get(id + str(i))['ids']) == 0:
                        collection.add(
                            documents=[chunk.page_content],
                            metadatas=[metadata],
                            ids=[id + str(i)]
                        )
                        print(".", end="")
                except:
                    print("x", end="")
                i += 1
        else:
            # Use chunks as-is,
            try:
                if len(collection.get(id + str(i))['ids']) == 0:
                    collection.add(
                        documents=[content],
                        metadatas=[metadata],
                        ids=[id + str(i)]
                    )
            except:
                print("x", end="")
            print("\nProcessing", title, iBook, "/", len(books), end="")
            for review in book['reviews']:
                i += 1
                try:
                    if len(collection.get(id + str(i))['ids']) == 0:
                        collection.add(
                            documents=[review['content']],
                            metadatas=[metadata],
                            ids=[id + str(i)]
                        )
                        print(".", end="")
                except:
                    print("x", end="")
    print("\nSize of", collection.name, "collection: ", collection.count())

def main():
    # Get the books
    books_file = open("books_file_4_test", "r")
    print("Loading books...")
    books = json.load(books_file)
    books_file.close()
    number_of_books = len(books)
    print("Loaded all", number_of_books, "books!")

    # Get the database
    database = VectorDatabase(path="./chromadb_test")
    client = database.getClient()
    # #####################################################################
    # # Use chunks as-is and all-MiniLM-L6-v2 embeddings (default)        #
    # #####################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/all-MiniLM-L6-v2')
    # collection = client.get_or_create_collection("asis_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection)
    # #####################################################################
    # # Use merge and chunks of 1000-50 chars and default Embeddings      #
    # #####################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/all-MiniLM-L6-v2')
    # collection = client.get_or_create_collection("chars1000-50_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 50)
    # #####################################################################
    # # Use merge and chunks of 500-50 chars and default Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars500-50_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 500, 50)
    # #####################################################################
    # # Use merge and chunks of 200-50 chars and default Embeddings       #
    # #####################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/all-MiniLM-L6-v2')
    # collection = client.get_or_create_collection("chars200-50_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 200, 50)
    # #####################################################################
    # # Use merge and chunks of 1000-100 chars and default Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars1000-100_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 100)
    # #####################################################################
    # # Use merge and chunks of 1000-200 chars and default Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars1000-200_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 200)
    #####################################################################
    # Use merge and chunks of 2000-50 chars and default Embeddings      #
    #####################################################################
    # collection = client.get_or_create_collection("chars2000-50_MiniLM-L6", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 2000, 50)
    # ##################################################################################
    # # USE DIFFERENT EMBEDDINGS: https://www.sbert.net/docs/pretrained_models.html    #
    # ##################################################################################
    # #####################################################################
    # # Use chunks as-is and all-mpnet-base-v2 embeddings         #
    # #####################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/all-mpnet-base-v2')
    # collection = client.get_or_create_collection("asis_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection)
    ####################################################################
    # Use merge and chunks of 1000-50 chars and all-mpnet-base-v2 Embeddings      #
    ####################################################################
    embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/all-mpnet-base-v2')
    collection = client.get_or_create_collection("chars1000-50_mpnet-base", embedding_function=embedding_function)
    storeBooksInCollection(books, collection, 1000, 50)
    # #####################################################################
    # # Use merge and chunks of 1000-100 chars and all-mpnet-base-v2 Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars1000-100_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 100)
    # #####################################################################
    # # Use merge and chunks of 1000-200 chars and all-mpnet-base-v2 Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars1000-200_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 200)
    # #####################################################################
    # # Use merge and chunks of 2000-50 chars and all-mpnet-base-v2 Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars2000-50_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 2000, 50)
    # #####################################################################
    # # Use merge and chunks of 500-50 chars and all-mpnet-base-v2 Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars500-50_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 500, 50)
    # #####################################################################
    # # Use merge and chunks of 200-50 chars and all-mpnet-base-v2 Embeddings       #
    # #####################################################################
    # collection = client.get_or_create_collection("chars200-50_mpnet-base", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 200, 50)
    # ##################################################################################
    # # Use chunks as-is and multi-qa-MiniLM-L6-dot-v1 embeddings                      #
    # ##################################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/multi-qa-MiniLM-L6-dot-v1')
    # collection = client.get_or_create_collection("asis_qa-MiniLM", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection)
    # ##################################################################################
    # # Use merge and chunks of 1000-50 chars and multi-qa-MiniLM-L6-dot-v1 Embeddings #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars1000-50_qa-MiniLM", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 50)
    # ##################################################################################
    # # Use merge and chunks of 500-50 chars and multi-qa-MiniLM-L6-dot-v1 Embeddings  #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars500-50_qa-MiniLM", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 500, 50)
    # ##################################################################################
    # # Use merge and chunks of 200-50 chars and multi-qa-MiniLM-L6-dot-v1 Embeddings  #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars200-50_qa-MiniLM", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 200, 50)
    # ##################################################################################
    # # Use chunks as-is and msmarco-distilbert-dot-v5 embeddings                      #
    # ##################################################################################
    # embedding_function = database.getSentenceTransformerEmbeddingFunction('sentence-transformers/msmarco-distilbert-dot-v5')
    # collection = client.get_or_create_collection("asis_distilbert-v5", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection)
    # ##################################################################################
    # # Use merge and chunks of 1000-50 chars and msmarco-distilbert-dot-v5 Embeddings #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars1000-50_distilbert-v5", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 50)
    # ##################################################################################
    # # Use merge and chunks of 500-50 chars and msmarco-distilbert-dot-v5 Embeddings  #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars500-50_distilbert-v5", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 500, 50)
    # ##################################################################################
    # # Use merge and chunks of 200-50 chars and msmarco-distilbert-dot-v5 Embeddings  #
    # ##################################################################################
    # collection = client.get_or_create_collection("chars200-50_distilbert-v5", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 200, 50)
    # #####################################################################
    # # Use chunks as-is and OpenAI embeddings (default)        #
    # #####################################################################
    # embedding_function = database.getOpenAIEmbeddings()
    # collection = client.get_or_create_collection("asis_ada-002", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection)
    # #####################################################################
    # # Use merge and chunks of 1000-50 chars and default Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars1000-50_ada-002", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 1000, 50)
    # #####################################################################
    # # Use merge and chunks of 500-50 chars and default Embeddings      #
    # #####################################################################
    # collection = client.get_or_create_collection("chars500-50_ada-002", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 500, 50)
    # #####################################################################
    # # Use merge and chunks of 200-50 chars and default Embeddings       #
    # #####################################################################
    # collection = client.get_or_create_collection("chars200-50_ada-002", embedding_function=embedding_function)
    # storeBooksInCollection(books, collection, 200, 50)

if __name__ == '__main__':
    main()
