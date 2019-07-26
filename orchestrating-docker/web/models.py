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


class Questions(db.Model):
    __tablename__ = 'questions'

    qid = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String, nullable = True)
    date_posted = db.Column(db.DateTime, nullable = True)

    def __init__(self, ques):
        self.ques = ques
        self.date_posted = datetime.datetime.now()

class Sessionid(db.Model):
    __tablename__ = 'sessionid'

    sessionId = db.Column(db.Integer, primary_key = True)
    lectuer = db.Column(db.String, nullable = True)
    status = db.Column(db.String, nullable = True)
    lecturer = db.Column(db.String, nullable = True)
    lecture = db.Column(db.String, nullable = True)
    term  = = db.Column(db.String, nullable = True)

    def __init__(self, sessionId, lecturer, lecture, term, status):
        self.sessionId = sessionId
        self.lecturer = lecturer
        self.lecture = lecture
        self.term = term
        self.status = status

class Responses(db.Model):
    __tablename__ = 'responses'

    Netid = db.Column(db.String, primary_key = True)
    session = db.Column(db.String, nullable = True)
    timespam = db.Column(db.String, nullable = True)
    question_num = db.Column(db.DateTime, nullable = True)
    
    def __init__(self, Netid, session, question_num):
        self.Netid = Netid
        self.session = session
        self.timespam = timespam

class UpVotes(db.Model):
    __tablename__ = 'upvotes'

    StNetid = db.Column(db.String, primary_key = True)
    quesId = db.Column(db.String, nullable = True)
    
    def __init__(self, StNetid, quesId):
        self.StNetid = StNetid
        self.quesId = quesId
       
class InstrQuestion(db.Model):
    __tablename__ = 'instrquestions'

    iqid = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String, nullable = False)
    optionA = db.Column(db.String, nullable = False)
    optionB = db.Column(db.String, nullable = True)
    optionC = db.Column(db.String, nullable = True)
    optionD = db.Column(db.String, nullable = True)
    answer = db.Column(db.String, nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False)

    def __init__(self, ques, a, b, c, d, answer):
        self.ques = ques
        self.optionA = a
        self.optionB = b
        self.optionC = c
        self.optionD = d
        self.answer = answer
        self.date_posted = datetime.datetime.now()
