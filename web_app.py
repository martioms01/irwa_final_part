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
from myapp.init_db import db
from datetime import datetime
import random

def _default(self, obj): # for using method to_json in objects
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default

app = Flask(__name__)                                           # instantiate the Flask application
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'        # random 'secret_key' is used for persisting data in secure cookie
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'                  # open browser dev tool to see the cookies

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/IRWA"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with SQLAlchemy
db.init_app(app)

# Create the tables defined in the models/ folder
with app.app_context():
    db.create_all()


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
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    # Log the previous document click
    save_doc_click(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    # Log the previous document click
    save_doc_click(session)                 
    
    search_query = request.form['search-query']
    search_id = analytics_data.save_query_terms(search_query)
    results = search_engine.search(search_query, search_id, corpus, token_tweets, inverted_index, tf, idf)
    
    found_count = len(results)
    session['last_search_query'] = search_query 
    session['last_found_count'] = found_count
    session['last_search_id'] = search_id 
            
    
    
    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    
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

    
    print(clicked_doc)
    
    return render_template('doc_details.html', document=document, doc_id=clicked_doc_id)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    # Log the previous document click
    save_doc_click(session) 

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
    

    return render_template('stats.html', clicks_data=docs)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    # Log the previous document click
    save_doc_click(session)

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

    return render_template('dashboard.html', visited_docs=visited_docs)


@app.route('/sentiment/<doc_id>', methods=['GET', 'POST'])
def sentiment_analysis(doc_id):
    # Set the session id and save it in the db
    set_session_id(session, request)
    # Log HTTP request data  
    analytics_data.log_http_request(session['session_id'], request) 
    # Log the previous document click
    save_doc_click(session)

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
    



def set_session_id(session, request):
    if 'session_id' not in session:
        session['session_id'] = random.randint(100, 999)
        user_ip = request.remote_addr    
        user_agent = request.headers.get('User-Agent')
        agent = httpagentparser.detect(user_agent)   
        analytics_data.track_user_context(session['session_id'], user_ip, user_agent) # Log User Context  

def save_doc_click(session):
    if 'doc_id_dwell_time' in session:
        doc_id, start_time = session['doc_id_dwell_time']
        analytics_data.log_click_on_document(session['session_id'], doc_id, start_time, session['last_search_query'])
        del session['doc_id_dwell_time']

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
