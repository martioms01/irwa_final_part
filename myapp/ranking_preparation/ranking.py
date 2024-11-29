from collections import defaultdict, Counter
import numpy as np
from numpy import linalg as la
from myapp.search.objects import Document

# Ranking

def conjunctive_filtering(query, documents):
    """
    Function for filtering the documents based on an input cojunctive query

    Args:
        query (list): A list of terms representing the input query.
        documents (_type_): A dictionary with document IDs as keys and lists of terms as values.
        
    Returns:
        Set containing the document ids of the documents that contain all the words of the query
    """

    # Set for storing the document id of the documents that contain all the words in the query
    valid_documents = set()

    for document_id, document_terms in documents.items():
        if all(query_term in document_terms for query_term in query):
            valid_documents.add(document_id)

    return valid_documents


def rank_documents_tf_idf(query, documents, inverted_index, tf, idf, document_filtering=None):
    """
    Function for ranking the documents based on an input query and using the tf-idf as the similarity metric  

    Args:
        query (list): A list of terms representing the input query.
        documents (dict): A dictionary with document IDs as keys and lists of terms as values.
        inverted_index (defaultdict(set)): An inverted index with terms as keys and sets of document IDs where those
        terms appear.
        tf (defaultdict(defaultdict(int))): Term frequency dictionary mapping document IDs to another dictionary that
        maps terms to their frequency in that document.
        idf (defaultdict(float)): Inverse document frequency dictionary mapping terms to their IDF values.
        document_filtering: (function, optional): A function to filter documents before ranking. Defaults to None.

    Returns:
        list: A list of tuples where each tuple contains a document ID and its similarity score to the query, sorted by
        score in descending order.
    """

    # Filter the documents if any filtered method specified
    candidate_docs = document_filtering(query, documents) if document_filtering is not None else set(doc_id for doc_id
                                                                                                     in documents.keys())

    # Dictionary mapping from doc_id to the vectorized document (only containing as many dimensions as words specified
    # in the query)
    vectorized_docs = defaultdict(lambda: [0] * len(query))
    
    # Array containing the vectorized query
    vectorized_query = [0] * len(query)

    # Counter with terms of the query and their respective counts
    query_terms_count = Counter(query)
    query_norm = la.norm(list(query_terms_count.values()))

    # Iterate over each term of the query, without repeating terms (i.e. for each distinct element of the query)
    for index, term in enumerate(query):
        
        vectorized_query[index] = query_terms_count[term] / query_norm * idf[term] 
        
        # For a document to be considered it has to be a candidate document and have the corresponding term.
        # If the term does not exist in the vocabulary it is not considered.
        for doc in (candidate_docs & inverted_index.get(term, set())):
            doc_norm = la.norm(list(tf[doc].values())) 
            vectorized_docs[doc][index] = tf[doc][term] / doc_norm * idf[term]

    # Compute the cosine similar between each document and the input query.
    doc_scores = [(doc, np.dot(vectorized_doc, vectorized_query)) for doc, vectorized_doc in vectorized_docs.items()]

    # Sort the documents by score
    doc_scores.sort(reverse=True, key=lambda doc_score: doc_score[1])


    return doc_scores 

