import json
import random

class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    
    def __init__(self):
        
        self.user_contexts = {}                             # To store request data such as IP, user agent, etc.
        self.queries = {}                                   # To track user queries
        self.fact_clicks = {}                               # To track document clicks
        self.sessions = {}                                  # To track user sessions
        self.http_requests = []                             # To track HTTP requests data
    
    

    def track_user_context(self, user_ip, user_agent): # TRACK REQUEST DATA
        context_id = random.randint(0, 100000)
        self.user_contexts[context_id] = {
            'ip': user_ip,
            'agent': user_agent,
            'timestamp': self.get_current_time()
        }
        return context_id
    
    
    def save_query_terms(self, terms: str) -> int:     # TRACK QUERIES
        #print(self) #GIVEN
        #return random.randint(0, 100000) #GIVEN
    
        query_id = random.randint(0, 100000)
        self.queries[query_id] = {'terms': terms, 'timestamp': self.get_current_time()}
        return query_id


    def save_click(self, doc_id, query_id, session_id):
        """
        Saves document clicks associated with queries and session.
        """
        if doc_id not in self.fact_clicks:
            self.fact_clicks[doc_id] = []
        self.fact_clicks[doc_id].append({
            'query_id': query_id,
            'session_id': session_id,
            'timestamp': self.get_current_time()
        })


"""    def save_dwell_time(self, doc_id, dwell_time):
        if doc_id not in self.document_dwell_times:
            self.document_dwell_times[doc_id] = []
        self.document_dwell_times[doc_id].append(dwell_time)
    
    @staticmethod
    def get_current_time():
        import datetime
        return datetime.datetime.now().isoformat()"""


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        json_data = self.to_json()
        return json.dumps(json_data)
