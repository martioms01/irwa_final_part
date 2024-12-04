import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from myapp.init_db import db

class Session(db.Model):
    __tablename__ = 'session'
    __table_args__ = {'extend_existing': True}  # Add this line

    session_id = db.Column(db.Integer, primary_key=True)  
    ip = db.Column(db.String, nullable=False)
    browser = db.Column(db.String, nullable=False)
    os = db.Column(db.String, nullable=False)
    device = db.Column(db.String, nullable=False)
    time_of_day = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    country = db.Column(db.String)
    city = db.Column(db.String)

    clicks = db.relationship('Click', backref='session', lazy=True)
    requests = db.relationship('Request', backref='session', lazy=True)

    def __repr__(self):
        return f'<Session {self.session_id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()