import nltk
import re
try:
    nltk.data.find('corpora/stopwords.zip')
except LookupError:
    nltk.download('stopwords')
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

## Preprocessing

def build_terms(line):
    """Prepocessing and tokenization of the tweets

    Args:
        line (str): tweet content

    Returns:
        List[str]: tokenized tweet content list
    """
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    symbols_to_remove = '!"$%&\'()*+,-/:;<=>?@[\\]^_`{|}~.'  # Does not include hashtag for future purposes
    url_pattern = re.compile(r'http\S+|www\S+')

    line = line.lower()  # Convert letters to lowercase
    
    urls = url_pattern.findall(line) # Find urls, save for latter and substitute with nothing
    line = url_pattern.sub('', line)

    line = line.translate(str.maketrans("", "", symbols_to_remove))  # Remove desired punctuation symbols
    line = line.split()  # Tokenize the text
    line = [word for word in line if word not in stop_words]  # Remove stopwords
    line = [stemmer.stem(word) for word in line]  # Perform stemming
    
    line.extend(urls)  # Add all found urls at the end
    
    return line

def create_tokenized_dictionary(documents):
    """Function to preprocesses tweets and maps them to a doc_id

    Args:
        tweets (Dict[id, Tweet]): dicitonary containing the mapping between tweet ids and tweet objects

    Returns:
        Dict[str, List[str]]: dicitonary mapping from document id to the tokenized tweet content
    """
    # Load the mapping of doc_id to tweet_id from the CSV file

    # Create tokenized dictionary with doc_id as key
    tokenized_dict = {}

    for id, doc in documents.items():
        tokenized_dict[id] = build_terms(doc.get_content())

    return tokenized_dict
