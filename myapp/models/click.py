from flask_sqlalchemy import SQLAlchemy
from myapp.init_db import db


class Click(db.Model):
    __tablename__ = 'click'
    __table_args__ = {'extend_existing': True}  # This allows modification of an existing table

    # Click ID will auto-increment by default since it is the primary key
    click_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id'), nullable=False)
    document_id = db.Column(db.String, nullable=False)
    query = db.Column(db.String)
    dwell_time = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Click {self.click_id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()