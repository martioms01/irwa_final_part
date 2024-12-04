import pandas as pd
from myapp.models.click import Click
from myapp.models.request import Request
from myapp.models.session import Session
from myapp.init_db import db

# Function to fetch all rows from the Click model and convert to a Pandas DataFrame
def get_all_clicks():
    # Use db.select() to create the select object and execute the query
    stmt = db.select(Click)  # Create the select statement
    result = db.session.execute(stmt)  # Execute the statement
    
    # Fetch all rows from the result
    clicks = result.scalars().all()  # 'scalars()' is used to fetch the rows as objects
    
    # Prepare the data as a list of dictionaries
    clicks_data = [
        {
            'document_id': c.document_id,  # Replace with the correct attribute names
            'query': c.query               # Replace with the correct attribute names
        }
        for c in clicks
    ]
    
    # Convert the list of dictionaries into a Pandas DataFrame
    df_clicks = pd.DataFrame(clicks_data)
    
    return df_clicks

# Function to fetch all rows from the Request model and convert to a Pandas DataFrame
def get_all_requests():
    # Fetch all rows from the Request table
    requests = Request.query.all()
    
    # Convert the result to a list of dictionaries (this is necessary for Pandas)
    requests_data = [{'request_id': r.request_id,
                      'session_id': r.session_id,
                      'url': r.url,
                      'referer': r.referer,
                      'timestamp': r.timestamp,
                      'method': r.method} for r in requests]
    
    # Convert the list of dictionaries to a Pandas DataFrame
    df_requests = pd.DataFrame(requests_data)
    
    return df_requests

# Function to fetch all rows from the Session model and convert to a Pandas DataFrame
def get_all_sessions():
    # Fetch all rows from the Session table
    sessions = Session.query.all()
    
    # Convert the result to a list of dictionaries (this is necessary for Pandas)
    sessions_data = [{'browser': s.browser} for s in sessions]
    
    # Convert the list of dictionaries to a Pandas DataFrame
    df_sessions = pd.DataFrame(sessions_data)
    
    return df_sessions
