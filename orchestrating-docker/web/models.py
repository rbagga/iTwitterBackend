# models.py


import datetime
from app import db


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True)

    def __init__(self, text):
        self.text = text
        self.date_posted = datetime.datetime.now()


class Question(db.Model):
    __tablename__ = 'questions'

    qid = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String, nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False)

    def __init__(self, text):
        self.text = text
        self.date_posted = dateime.datetime.now()
