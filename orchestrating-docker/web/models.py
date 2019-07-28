# models.py


from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig

# from sqlalchemy import func, select, text
# app = Flask(__name__)
import datetime
from app import db
# db = SQLAlchemy(app)

class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True)

    def __init__(self, text):
        self.text = text
        self.date_posted = datetime.datetime.now()



#refers to questions asked by students
class Question(db.Model):
    __tablename__ = 'questions'

    qid = db.Column(db.Integer, primary_key = True)
    sessionid = db.Column(db.Integer)
    ques = db.Column(db.String, nullable = True)
    upvotes = db.Column(db.Integer, nullable = False)
    date_posted = db.Column(db.DateTime, nullable = True)

    def __init__(self, ques, sessionid, upvotes=0):
        self.ques = ques
        self.sessionid = sessionid
        self.date_posted = datetime.datetime.now()
        self.upvotes = upvotes

# class Question(db.Model):
#     __tablename__ = 'questions'
#
#     qid = db.Column(db.Integer, primary_key = True)
#     ques = db.Column(db.String, nullable = True)
#     date_posted = db.Column(db.DateTime, nullable = True)
#
#     def __init__(self, ques):
#         self.ques = ques
#         self.date_posted = datetime.datetime.now()


class Upvotes(db.Model):
    __tablename__ = 'upvotes'

    netid = db.Column(db.String, primary_key = True)
    qid = db.Column(db.Integer, nullable = False)

    def __init__(self, netid, qid):
        self.netid = netid
        self.qid = qid
class Session(db.Model):
    __tablename__ = 'session'
    sessionsId = db.Column(db.Integer, primary_key = True)
    sessionId = db.Column(db.Integer, nullable = True)
    # professor = db.Column(db.String, nullable = True)
    startTime = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String, nullable = True)
    professor = db.Column(db.String, primary_key = False)
    classID = db.Column(db.String, primary_key = False)
    term  = db.Column(db.String, primary_key = False)

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

class IclickerReponse(db.Model):
    __tablename__ = 'studentquestionanswer'

    reponse = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String, nullable = False)
    sessionId = db.Column(db.Integer, nullable = False)
    questionId = db.Column(db.Integer, nullable = False)
    studentreponse = db.Column(db.String, nullable = True)
    responsetimes = db.Column(db.DateTime, nullable = False)

    def __init__(self, netid, sessionId, questionId, studentreponse):
        self.netid = netid
        self.sessionId = sessionId
        self.questionId = questionId
        self.studentreponse = studentreponse
        self.responsetimes = datetime.datetime.now()


class InstrQuestion(db.Model):
    __tablename__ = 'instrquestions'

    iqid = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String, nullable = False)
    optionA = db.Column(db.String, nullable = False)
    optionB = db.Column(db.String, nullable = True)
    optionC = db.Column(db.String, nullable = True)
    optionD = db.Column(db.String, nullable = True)
    answer = db.Column(db.String, nullable = False)
    #sessionId number between 1 - 41, total number of lecture in semester
    sessionId = db.Column(db.Integer, nullable = True)
    date_posted = db.Column(db.DateTime, nullable = False)

    def __init__(self, ques, answer, optionA, sessionId ,optionB='None', optionC='None', optionD='None'):
        self.ques = ques
        self.optionA = optionA
        self.optionB = optionB
        self.optionC = optionC
        self.optionD = optionD
        self.answer = answer
        self.sessionId = sessionId
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
