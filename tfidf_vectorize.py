import json
import os.path

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import math
from english_words import get_english_words_set
import pickle


# Given a word word_clean removes characters that exist in string dirt (!@#$%^&*()_+~<>?:|}{,.';[]") for a word and returns it
def word_clean(word):
    dirt = '''!@#$%^&*()_+~<>?:|}{,.';[]"'''
    clean_word = ''.join(char for char in word if char not in dirt)
    return clean_word

# Cleans every word in a list of words
def list_clean(list):
    clean_list = []
    for word in list:
        clean_list.append(word_clean(word))
    return clean_list

# Cleans every word in a list of lists
def lists_clean(lists):
    print("Cleaning lists", len(lists), end="")
    clean_lists = []
    i = 0
    for list in lists:
        i += 1
        if i%100 == 0:
            print(".", end="")
        clean_lists.append(list_clean(list))
    print("done!")
    return clean_lists

# Given a list of lists and a list of stopwords it removes all the stopwords and returns a list of lists
def remove_stop_lists(lists,stopwords,web2lowerset):
    print("Removing stop words", len(lists), end="")
    nostop_lists = []
    english = '''abcdefghijklmnopqrstuvwxyz'''
    english_words = web2lowerset
    i = 0;
    for list in lists:
        i += 1
        if i%100 == 0:
            print(".", end="")
        nostop_list = [word for word in list if word != '' and word[0] in english and word not in stopwords and word in english_words]
        nostop_lists.append(nostop_list)
    print("done!")
    return nostop_lists

# Given a word and a stemmer, returns a stemmed word
def stem(word, stemmer):
    stemmed_word = stemmer.stem(word)
    return stemmed_word

# Given a list of lists of words and a stemmer, returns a list of lists of stemmed words
def stem_lists(lists, stemmer):
    print("Stemming", end="")
    stemmed_lists = []
    i = 0
    for list in lists:
        i += 1
        if i%100 == 0:
            print(".", end="")
        stemmed_list = [stem(word, stemmer) for word in list]
        stemmed_lists.append(stemmed_list)
    print("done!")
    return stemmed_lists

# Given a list of lists, returns a single list
def lists_to_list(lists):
    flat = []
    for list in lists:
        flat += list
    return flat

# Given a list of words (vocabulary) and a list of lists (every list under the list is a bag of every word in a document)
# Returns a list of lists for (i) word frequency, (ii) tf, (iii) tfidf and (iv) idf
# Creating word weights as per { Wij =  tfij * idfi  =  tfij * log2(N/ dfi) }, 
# { tfij =  fij  / maxi{fij} } , { idfi = log2(N/ df i) }
# for i term in vocabulary and j document
#
# For example table_tfidf returns: 
# [[W11,W12,W13,...,W1n],
# [W21,W22,W23,...,W2n],
# ...,
# [Wn1,Wn2,Wn3,...,Wnn]]
#
# table_idf returns:
# [idf1, idf2,...,idfn]
def tfidf_tables(vocabulary, lists):
    print("Running tf-idf analysis...", len(vocabulary), end="")
    table_f = []
    doc_f_list = []
    # Creating table_f:
    # [[f11,f12,...,fin],
    # [f21,f22,...,f1n],
    # ...,
    # [fn1,fn2,...,fnn]]
    # Creating doc_f_list:
    # [[df1],
    # [df2],
    # ...,
    # [dfn]]
    # dfi = number of documents containing term i
    i = 0
    for token in vocabulary:
        i += 1
        if i%10 ==0:
            print(".", end="")
        if i%100 ==0:
            print("")
            print(i, '/', len(vocabulary))
        token_f = []
        doc_f = 0
        for list_a in lists:
            count_f = list_a.count(token)
            token_f += [count_f]
            if count_f > 0:
                doc_f += 1
        table_f.append(token_f)
        doc_f_list.append(doc_f)

    max_f_list = []
    # creating the max(fij)
    # max_f_list returns:
    # [[max(fi1)],[max(fi2)],...,[max(fin)]]
    max_f = 0
    a = 'good'
    for index, token_f in enumerate(table_f): # for fij in table_fij
        if a == 'Break':
            break
        try:
            max_f = max(token_f)
            if max_f == 0:
                print(index)
                a = 'Break'
            max_f_list.append(max_f)
        except Exception as e:
            print(e)
            print(index)
            a = 'Break'
            break

    if a == 'Break':
        print('e')
        return

    table_tf = []
    # Creating table_tf:
    # [[tf11,tf12,...,tfin],
    # [tf21,tf22,...,tf1n],
    # ...,
    # [tfn1,tfn2,...,tfnn]] 
    for token_f in table_f: # For j in documents:
        table_tf.append([f/max_f_list[index] for index,f in enumerate(token_f)]) # For i term in j document: tfij = fij / max(fij)
    
    # Creating table_idf:
    # [idf1, idf2,...,idfn]
    table_idf = [math.log2(len(lists)/df) for df in doc_f_list] # For dfi: idfi = log2( N / dfi ) , N = len(lists) = n

    table_tfidf = []
    # Creating table_tfidf:
    # [[tfidf11,tfidf12,...,tfidfin],
    # [tfidf21,tfidf22,...,tfidf1n],
    # ...,
    # [tfidfn1,tfidfn2,...,tfidfnn]]
    for index, idfi in enumerate(table_idf): # For j and idfi: 
        for j in range(len(table_tf[index])):
            token_tfidf = [tf*idfi for tf in table_tf[index]] # For tfij: tfidfij = tfij * idfi
        table_tfidf.append(token_tfidf)
    print("done!")
    return table_f, table_tf, table_tfidf, table_idf




def main():
    filename = 'books_file_4_200'
    vocab = []
    vocab_lists = []
    if not os.path.exists('vocab'+filename+'.pkl') or not os.path.exists('vocab_lists'+filename+'.pkl'):

        # Open the books_file.json
        # Directory\file.json could be user input (maybe)
        with open(filename) as file:
            data = json.load(file)

        book_dict = {}
        # Populate a dictionary with {key: title1 , value: content1}
        # Oportunity to assign more weight to title or author etc.
        print("Reading", len(data), "books")
        for book in data:
            print(".", end="")
            if book['title']: # ignore empty entries
                title = book['title']
                content = book['description'] + " " + ', '.join(review['content'] for review in book['reviews'])
                if content: # ignore empty entries
                    book_dict[title] = content
        print("read!")
        print("Splitting...", end="")
        # Creating a list of lists:
        # [[content1.split()],[content2.split()],...,[contentn.split()]]
        token_list = []
        for key, value in book_dict.items():
            token_list.append(value.split())
        print("done!")


        web2lowerset = get_english_words_set(['web2'], lower=True)
        nltk.download('stopwords')
        stop_words = stopwords.words('english')
        stemmer = PorterStemmer()

        # Cleaing words, removing stopwords and steming each word for the list of lists
        vocab_lists = stem_lists(remove_stop_lists(lists_clean(token_list), stop_words, web2lowerset), stemmer)

        # Deleting empty entries after stemming
        to_delete = []
        for index, vocab_list in enumerate(vocab_lists):
            if vocab_list:
                continue
            else:
                to_delete.append(index)

        for index in to_delete:
            del book_dict[list(book_dict.keys())[index]]
            vocab_lists.pop(index)

        # Turning the list of lists to a single list with unique words
        vocab = list(set(lists_to_list(vocab_lists)))

        with open('vocab' + filename + '.pkl', 'wb') as fp:
            pickle.dump(vocab, fp)
        with open('vocab_lists' + filename + '.pkl', 'wb') as fp:
            pickle.dump(vocab_lists, fp)
    else:
        with open('vocab' + filename + '.pkl', 'rb') as fp:
            vocab = pickle.load(fp)
        with open('vocab_lists' + filename + '.pkl', 'rb') as fp:
            vocab_lists = pickle.load(fp)

    # Creating tables
    table_f, table_tf, table_tfidf, table_idf = tfidf_tables(vocab, vocab_lists)


    tfidf_dict = {'book dict': book_dict, 'vocabulary': vocab, 'IDFs': table_idf, 'TFIDFs': table_tfidf}
    with open("tfidf_dict_4_200.json", "w") as outfile:
        json.dump(tfidf_dict, outfile)

    return


if __name__ == '__main__':
    main()
