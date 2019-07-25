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
    ques = db.Column(db.String, nullable = True)
    date_posted = db.Column(db.DateTime, nullable = True)

    def __init__(self, ques):
        self.ques = ques
        self.date_posted = datetime.datetime.now()

class Session(db.Model):
    __tablename__ = 'session'

    sessionId = db.Column(db.Integer, primary_key = True)
    # professor = db.Column(db.String, nullable = True)
    startTime = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String, nullable = True)
    professor = db.Column(db.String, nullable = False)
    classID = db.Column(db.String, nullable = False)
    term  = db.Column(db.String, nullable = False)

    def __init__(self, professor, classID, term, status='Scheduled'):
        # self.sessionId = sessionId
        self.professor = professor
        self.classID = classID
        '''change this later to be date time input by user!!!'''
        self.startTime = datetime.datetime.now()

        # self.lecture = lecture
        self.term = term
        self.status = status

class Responses(db.Model):
    __tablename__ = 'responses'

    responseID = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String, nullable = False)
    session = db.Column(db.String, nullable = False)
    timestamp = db.Column(db.String, nullable = False)
    question_num = db.Column(db.DateTime, nullable = False)
    response = db.Column(db.String, nullable = True)

    def __init__(self, netid, session, question_num, response=False):
        self.netid = netid
        self.session = session
        self.question_num = question_num
        self.response = response
        self.timestamp = datetime.datetime.now()


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

    def __init__(self, ques, answer, a, b=None, c=None, d=None):
        self.ques = ques
        self.optionA = a
        self.optionB = b
        self.optionC = c
        self.optionD = d
        self.answer = answer
        self.date_posted = datetime.datetime.now()

class QuestionStatus(db.Model):
    __tablename__ = 'questionstatus'

    qStatusID = db.Column(db.Integer, primary_key = True)
    sessionID = db.Column(db.Integer, nullable=True)
    questionNum = db.Column(db.Integer, nullable=True)
    startTime = db.Column(db.DateTime, nullable = True)
    endTime = db.Column(db.DateTime, nullable = True)

    def __init__(self, questionNum, sessionID=None, startTime=None, endTime=None):
        self.questionStatusKey = db.Column(db.Integer, primary_key = True)
        self.sessionID = sessionID
        self.questionNum = questionNum
        self.startTime  = startTime
        self.endTime = endTime
