import random

from myapp.search.objects import ResultItem, Document
from myapp.search.algorithms import search_in_corpus

def build_demo_results(corpus: dict, search_id):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)
    ll = list(corpus.values())
    for index in range(random.randint(0, 40)):
        item: Document = ll[random.randint(0, size - 1)]
        res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), random.random()))

    # for index, item in enumerate(corpus['Id']):
    #     # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
    #     res.append(DocumentInfo(item.Id, item.Tweet, item.Tweet, item.Date,
    #                             "doc_details?id={}&search_id={}&param2=2".format(item.Id, search_id), random.random()))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res


class SearchEngine:
    """educational search engine"""

    def search(self, search_query, search_id, corpus, token_tweets, inverted_index, tf, idf):
        print("Search query:", search_query)

        results = []
        ##### your code here #####
        #results = build_demo_results(corpus, search_id)  # replace with call to search algorithm

        #results = search_in_corpus(search_query)
        ##### your code here #####
        res = search_in_corpus(search_query, token_tweets, inverted_index, tf, idf)
        res = [(corpus[doc_id], score) for doc_id, score in res]
        for item, scores in res:
            results.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), item.url, scores))

        results.sort(key=lambda doc: doc.ranking, reverse=True)

        return results
