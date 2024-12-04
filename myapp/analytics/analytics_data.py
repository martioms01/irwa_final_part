import json
import random
import httpagentparser
from datetime import datetime
import requests

from myapp.models.session import Session
from myapp.models.click import Click
from myapp.models.request import Request

class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    
    def __init__(self):
        
        
        self.http_requests = {}                             # To track HTTP requests data
        self.user_context = {}                              # Specifically stores browser, OS/computer/mobile, time of the day, date, IP address, country, city
        self.queries = {}                                   # To track user queries
        self.fact_clicks = {}                               # To track document clicks {doc_id: ClickedDoc}
        self.total_session_clicks = -1                      # This way we set the value to 0 on startup, and can add later session clicks.
    
    @staticmethod
    def get_current_time():
        import datetime
        return datetime.datetime.now().isoformat()    
    
    
    def log_http_request(self, session_id, request):
        """
        Logs an HTTP request with details such as IP, user-agent, method, URL, and referrer.
        
        :param request: The Flask request object.
        :return: None
        """

        new_request = Request(session_id=session_id, url=request.url, referer=request.referrer if request.referrer else "Direct", timestamp=self.get_current_time(), method=request.method)
        new_request.save()

        context_id = random.randint(0, 100000)
        self.http_requests[context_id] = {
            'ip': request.remote_addr,
            'agent': httpagentparser.detect(request.headers.get('User-Agent')),
            'method': request.method,
            'url': request.url,
            'referrer': request.referrer if request.referrer else "Direct",
            'timestamp': self.get_current_time()
        }  

    
    def track_user_context(self, session_id, user_ip, user_agent):
        """
        Tracks the user context including browser, OS, device, time of the day, IP address, country, and city.
        
        :param user_ip: The user's IP address
        :param user_agent: The User-Agent string (used to extract browser, OS, and device)
        :return: A unique context ID
        """
        
        agent = httpagentparser.detect(user_agent)
        browser = agent.get("browser", {}).get("name", "Unknown")  # Use 'name' for browser
        os = agent.get("os", {}).get("name", "Unknown")  # Use 'name' for OS
        device = agent.get("device", {}).get("family", "Unknown")  # Use 'family' for device
        
        def get_time_of_day():
            current_time = datetime.now()
            hour = current_time.hour
            if hour < 12:
                return "Morning"
            elif hour < 18:
                return "Afternoon"
            else:
                return "Evening"
        time_of_day = get_time_of_day()
        timestamp = self.get_current_time()

        def get_location(ip_address):                                         # Use a free API to get country and city based on IP
            try:
                response = requests.get(f'https://ipinfo.io/{ip_address}/json')
                data = response.json()
                country = data.get("country")
                city = data.get("city")
                return country, city
            except Exception as e:
                return "Unknown/Private", "Unknown/Private"
        country, city = get_location(user_ip)

        new_session = Session(session_id=session_id, ip=user_ip, browser=browser, os=os, device=device, time_of_day=time_of_day, timestamp=timestamp, country=country, city=city)
        new_session.save()

        context_id = session_id
        self.user_context[context_id] = {
            'ip': user_ip,
            'browser': browser,
            'os': os,
            'device': device,
            'time_of_day': time_of_day,
            'timestamp': timestamp,
            'country': country,
            'city': city
        }

        return context_id
    
    def save_query_terms(self, terms: str) -> int: 

        query_id = random.randint(0, 100000)
        self.queries[query_id] = {'terms': terms, 'timestamp': self.get_current_time()}
        return query_id
    
    def log_click(self):
        self.total_session_clicks += 1

    def log_click_on_document(self, session_id, doc_id, start_time, query):
        self.log_click()
        if doc_id in self.fact_clicks:
            clicked_doc = self.fact_clicks[doc_id]
            end_time = datetime.now()
            start_time = datetime.fromisoformat(start_time)
            dwell_time = (end_time - start_time).total_seconds()
            clicked_doc.dwell_time = dwell_time

            new_click = Click(session_id=session_id, document_id=doc_id, query=query, dwell_time=dwell_time)
            new_click.save()
    





class ClickedDoc:
    def __init__(self, doc_id, query):
        self.doc_id = doc_id
        self.queries = {query:1}
        self.dwell_time = 0

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        json_data = self.to_json()
        return json.dumps(json_data)
