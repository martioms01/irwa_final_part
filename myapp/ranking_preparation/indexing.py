from collections import defaultdict
import numpy as np
# Indexing

def create_inverted_index(token_tweets):
    """
    Creates an inverted index from a collection of tokenized documents.

    Args:
        token_tweets (dict): A dictionary where keys are document IDs and values are lists of tokens (words) in each document.

    Returns:
        defaultdict(set): An inverted index where keys are tokens and values are sets of document IDs in which each token appears.
    """

    inverted_index = defaultdict(set)
    
    # Iterate over each document
    for doc_id, tokens in token_tweets.items():
        # For each token in the document
        for token in tokens:
            # Append the document ID to the token's set
            inverted_index[token].add(doc_id)
    
    return inverted_index




def create_inverted_index_tf_idf(documents):
    """
    Creates an inverted index and calculates term frequency (TF) and inverse document frequency (IDF) for each term.

    Args:
        documents (dict): A dictionary where keys are document IDs and values are lists of terms in each document.

    Returns:
        tuple: A tuple containing:
            - inverted_index (defaultdict(set)): An inverted index mapping terms to sets of document IDs containing
            those terms.
            - tf (defaultdict(defaultdict(int))): A dictionary mapping each document ID to another dictionary that maps
            terms to their frequencies in that document.
            - idf (defaultdict(float)): A dictionary mapping terms to their inverse document frequency across all
            documents.
    """

    # Create inverted index
    inverted_index = create_inverted_index(documents)

    num_documents = len(documents)
    
    # Dictionary containing as keys the doc_id and as values a dictionary containing as key the term and as value the
    # frequency of the term in the doc_id
    tf = defaultdict(lambda: defaultdict(int))
    
    # Dictionary containing as keys the terms and as values the document frequency of such terms
    df = defaultdict(int)
    
    # Dictionary containing as keys the terms and as values the inverse document frequency of such terms
    idf = defaultdict(float)

    for doc_id, content in documents.items():
        for term in content:
            tf[doc_id][term] += 1

    for term, values in inverted_index.items():
        # The document frequency of a term is the length of the set value in the inverted index
        df[term] = len(values)
        # Compute the idf as the logarithm of the division between the number of documents and the document frequency
        idf[term] = np.round(np.log(float(num_documents / df[term])), 4)

    return inverted_index, tf, idf