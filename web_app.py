import os
from json import JSONEncoder
import httpagentparser  # get user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request
from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
import myapp.ranking_preparation.preprocessing as pp
import myapp.ranking_preparation.indexing as ix
from datetime import datetime

def _default(self, obj): # for using method to_json in objects
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default

app = Flask(__name__)                                           # instantiate the Flask application
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'        # random 'secret_key' is used for persisting data in secure cookie
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'                  # open browser dev tool to see the cookies
search_engine = SearchEngine()                                  # instantiate our search engine
analytics_data = AnalyticsData()                                # instantiate our in memory persistence

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
file_path = path + "/data/farmers-protest-tweets.json"          # load documents corpus into memory.
corpus = load_corpus(file_path)
token_tweets = pp.create_tokenized_dictionary(corpus)
inverted_index, tf, idf = ix.create_inverted_index_tf_idf(token_tweets)


# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")                             
    
    session['some_var'] = "IRWA 2021 home"                      # flask server creates a session by persisting a cookie in the user's browser.
                                                                # the 'session' object keeps data between multiple requests

    user_agent = request.headers.get('User-Agent')
    agent = httpagentparser.detect(user_agent)    
    user_ip = request.remote_addr    
    analytics_data.log_http_request(request)                    # Log HTTP request data
    analytics_data.track_user_context(user_ip, user_agent)      # Log User Context
    analytics_data.total_session_clicks +=1                     # Add session clicks
    
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        if doc_id in analytics_data.fact_clicks:
            clicked_doc = analytics_data.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time += dwell_time
            print(f"Document ID={doc_id} dwell time updated: {dwell_time} seconds")

        del session['doc_id_dwell_time']

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    
    search_query = request.form['search-query']
    search_id = analytics_data.save_query_terms(search_query)
    results = search_engine.search(search_query, search_id, corpus, token_tweets, inverted_index, tf, idf)
    
    found_count = len(results)
    session['last_search_query'] = search_query 
    session['last_found_count'] = found_count
    session['last_search_id'] = search_id 
            
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        if doc_id in analytics_data.fact_clicks:
            clicked_doc = analytics_data.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time += dwell_time
            print(f"Document ID={doc_id} dwell time updated: {dwell_time} seconds")

        del session['doc_id_dwell_time']
    
    analytics_data.log_http_request(request)                    # Log HTTP request data
    analytics_data.total_session_clicks +=1                     # Add session clicks
    
    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():

    res = session["some_var"]
    
    clicked_doc_id = request.args["id"]                         # get the query string parameters from request
    search_query = session['last_search_query']
                
    print(f"Click on document with ID={clicked_doc_id}, related to Query='{search_query}'")

    document = corpus[int(clicked_doc_id)]
    if clicked_doc_id in analytics_data.fact_clicks:
        clicked_doc = analytics_data.fact_clicks[clicked_doc_id]                   # If document exists, retrieve the ClickedDoc and increment counter
        if search_query in clicked_doc.queries:
            clicked_doc.queries[search_query] += 1
        else:
            clicked_doc.queries[search_query] = 1
    else:
        clicked_doc = ClickedDoc(clicked_doc_id, search_query)                      # If it's a new document, create a new ClickedDoc and add it
        
        
    session['doc_id_dwell_time'] = (clicked_doc_id, datetime.now().isoformat())                                        # Save the current document ID in the session

    analytics_data.fact_clicks[clicked_doc_id] = clicked_doc
    analytics_data.log_http_request(request)                                       # Log HTTP request data
    analytics_data.total_session_clicks +=1                                        # Add session clicks
    
    print(clicked_doc)
    
    return render_template('doc_details.html', document=document, doc_id=clicked_doc_id)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """
    
    print(analytics_data.total_session_clicks)

    docs = []
    # ### Start replace with your code ###

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    
    analytics_data.log_http_request(request)                    # Log HTTP request data
    analytics_data.total_session_clicks +=1                     # Add session clicks
    
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        if doc_id in analytics_data.fact_clicks:
            clicked_doc = analytics_data.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time += dwell_time
            print(f"Document ID={doc_id} dwell time updated: {dwell_time} seconds")

        del session['doc_id_dwell_time']

    return render_template('stats.html', clicks_data=docs)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    print("Keys in fact_clicks:", analytics_data.fact_clicks.keys())  # Debugging output

    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = ClickedDoc(d.id, d.description, count)
        #print(f"Appending doc_id: {d.id}, description: {d.description}, counter: {analytics_data.fact_clicks[doc_id]}")  # Debugging output

        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.count, reverse=True)

    visited_docs = [doc.__str__() for doc in visited_docs]
    
    analytics_data.log_http_request(request)                    # Log HTTP request data
    analytics_data.total_session_clicks +=1                     # Add session clicks
    
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        if doc_id in analytics_data.fact_clicks:
            clicked_doc = analytics_data.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time += dwell_time
            print(f"Document ID={doc_id} dwell time updated: {dwell_time} seconds")

        del session['doc_id_dwell_time']

    return render_template('dashboard.html', visited_docs=visited_docs)


@app.route('/sentiment/<doc_id>', methods=['GET', 'POST'])
def sentiment_analysis(doc_id):
    document = corpus[(int(doc_id))]
    if not document:
        return "Document not found", 404
    
    if request.method == 'POST':
        # Perform sentiment analysis
        nltk.download('vader_lexicon')
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sid = SentimentIntensityAnalyzer()
        text = document.description
        score = sid.polarity_scores(str(text))['compound']
        return render_template('sentiment.html', score=score, document=document)
    
    # For `GET`, render the page with only the document details
    
    analytics_data.log_http_request(request)                    # Log HTTP request data
    analytics_data.total_session_clicks +=1                     # Add session clicks
    
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        if doc_id in analytics_data.fact_clicks:
            clicked_doc = analytics_data.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time += dwell_time
            print(f"Document ID={doc_id} dwell time updated: {dwell_time} seconds")

        del session['doc_id_dwell_time']

    return render_template('sentiment.html', document=document)

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
