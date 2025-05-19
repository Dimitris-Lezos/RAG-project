# Book Recomendation RAG System
This project implements a book recommendation system where it receives a user **Query** 
and tries to match it over a database of **Book Reviews** it has scrapped from https://goodreads.com

* The query is firstly passed to **OpenAI LLM** to identify if a specific *Author* or *Genre* is requested.
* Then **OpenAI LLM** is used to split a long query or generate an additional similar query for a short one.
* Each Query is then represented by an embeddeding and matched to books' reviews stored in a **Vector Database**
* The top 10 reviews are passed to **OpenAI LLM** which selects the most appropriates

Several embeddings where tested for various with chunk sizes and overlapping characters to select `1000-50` with `sentence-transformers/all-mpnet-base-v2` as the best one for this project. 

File **SystemRAG.py** contains the implementation of the main engine.
File **VectorizeBooks.py** contains the code that creates the books database.
File **GoodReadsCrawl.py** contains the code used to scrap the books site.