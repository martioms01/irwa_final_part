import pandas as pd
import nltk
import re
try:
    nltk.data.find('corpora/stopwords.zip')
except LookupError:
    nltk.download('stopwords')
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import defaultdict, Counter
import numpy as np
from numpy import linalg as la
import myapp.ranking_preparation.ranking as ra
import myapp.ranking_preparation.preprocessing as pp



def search_in_corpus(query,token_tweets, inverted_index, tf, idf):
    # 1. create create_tfidf_index
    
    ranked_documents_tf_idf = ra.rank_documents_tf_idf(pp.build_terms(query), token_tweets, inverted_index, tf, idf, document_filtering=ra.conjunctive_filtering)

    # 2. apply ranking
    return ranked_documents_tf_idf
