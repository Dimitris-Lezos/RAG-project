import json
from nltk.stem import PorterStemmer
import numpy as np
from numpy import dot
from numpy.linalg import norm


# Given a word and a stemmer, returns a stemmed word
def stem(word, stemmer):
    stemmed_word = stemmer.stem(word)
    return stemmed_word

# Vectorize query, given query, vocabulary, vocabulary idf, ans a stemmer
def q_to_v(q,vocabulary,idf_list,stemmer):
    qs = np.array([stem(word, stemmer) for word in q.split()])# Stemming the query
    qs_f = np.zeros(len(vocabulary))
    for word in qs:
        try:
            qs_f[np.where(vocabulary == word)[0][0]] += 1
        except:
            continue
    maxf = max(qs_f)
    if maxf != 0:
        qs_tf = np.zeros(len(vocabulary))
        # Query term frequency: count of each term / max count of terms
        qs_tf = qs_f/maxf
        qs_tfidf = np.zeros(len(vocabulary))
        # Query term tfidf: query term tf * term idf
        qs_tfidf = qs_tf*idf_list
        return qs_tfidf
    else:
        return False

# CosSim(dj, q)
# cosine similraity of document j and query q
def cossim(dj,q):
    norm_dj = norm(dj)
    norm_q = norm(q)
    if norm_dj == 0 or norm_q == 0:
        return 0
    return dot(dj, q)/(norm_dj*norm_q)

# Need to turn:
# [[11,12,..,1n],
# [21,22,...,2n],
# ...,
# [n1,n2,...,nn]]
# To:
# [[11,21,...,n1],
# [12,22,...,n2],
# ...,
# [1n,2n,...,nn]]
def reverse_lists(lists):
    return np.array(lists).T

# Takes query, vocabulary, term idf, the table of tfidf and a stemmer
# and returns a list with cosine similarity that looks like:
# [[1, cosine similarity(1,query)],
# [2, cosine similarity(2,query)],
# ...,
# [n, cosine similarity(n,query)]]
def comp_relevance(q, vocabulary, idf_list, table_tfidf, stemmer):
    qs_tfidf = q_to_v(q,vocabulary,idf_list, stemmer) #query to vector
    if np.any(qs_tfidf) != False:
        rel_list = []
        books_n = len(table_tfidf)
        for j in range(books_n): #for j:
            rel_list.append([j, cossim(table_tfidf[j], qs_tfidf)])
            # rel_list = [j, cosine similarity(document j tfidf vector, query tfidf vector)]
        rel_list = sorted(rel_list, key=lambda x: x[1], reverse=True) # Sorting the list by similarity
        if books_n > 9.5:
            result_n = 10
        else:
            result_n = books_n
        return rel_list[:result_n]
    else:
        return False

# Takes a relevance list and prints titles (can be expanded to print more info)
def rel_results(rel_list, titles, book_dict):
    rank = 1
    results = []
    for i,x in rel_list:
        result = {
            "title": titles[i],
            "content": book_dict[titles[i]][:500]
        }
        #results.append(f"\nResult {rank}: \n Title: {titles[i]} \nDescription: \n {book_dict[titles[i]][:500]}...")
        results.append(result)
        rank += 1
    return results


def main():

    print('Initializing...')
    with open('tfidf_dict_4_200.json', 'r') as file:
        data = json.load(file)
    print("Loaded", len(data['book dict']), "books")


    stemmer = PorterStemmer()
    vocab = np.array(data['vocabulary'])
    table_idf = np.array(data['IDFs'])
    table_tfidf = reverse_lists(data['TFIDFs'])
    book_dict = data['book dict']
    titles = list(book_dict.keys())
    print('Finished Loading!')


    while True:
        try:
            query = input('Search for books (empty to end): ')
            if query == '':
                break
            relevance_results = comp_relevance(query,vocab,table_idf,table_tfidf, stemmer)
            if relevance_results == False:
                print('No results! Try a different query!')
            else:
                print('Getting Results...')
                results = rel_results(relevance_results, titles, book_dict)
                for result in results:
                    print(result)
        except Exception as e:
            print(e)
            break

    return

if __name__ == '__main__':
    main()
    







