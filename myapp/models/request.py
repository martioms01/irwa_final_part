from flask_sqlalchemy import SQLAlchemy
from myapp.init_db import db


class Request(db.Model):
    __tablename__ = 'request'
    __table_args__ = {'extend_existing': True}  # This allows modification of an existing table

    # Set request_id to auto-increment
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    url = db.Column(db.String, nullable=False)
    referer = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.Date, nullable=False)
    method = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Request {self.request_id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()