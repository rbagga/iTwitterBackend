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
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, text, readts, writets):
        self.text = text
        self.date_posted = datetime.datetime.now()
        self.readts = readts
        self.writets = writets



#refers to questions asked by students
class Question(db.Model):
    __tablename__ = 'questions'

    qid = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String, nullable = False)
    sessionid = db.Column(db.Integer)
    ques = db.Column(db.String, nullable = True)
    upvotes = db.Column(db.Integer, nullable = False, default = 0)
    date_posted = db.Column(db.DateTime, nullable = True)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, netid, ques, sessionid, upvotes, readts, writets):
        self.ques = ques
        self.netid = netid
        self.sessionid = sessionid
        self.date_posted = datetime.datetime.now()
        self.upvotes = upvotes
        self.readts = readts
        self.writets = writets

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
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, netid, qid, readts, writets):
        self.netid = netid
        self.qid = qid
        self.readts = readts
        self.writets = writets

class Session(db.Model):
    __tablename__ = 'session'
    sessionid = db.Column(db.Integer, primary_key = True)
    startTime = db.Column(db.DateTime, nullable = True)
    status = db.Column(db.String, nullable = False, default='Scheduled')
    classid = db.Column(db.String, nullable = False)
    term  = db.Column(db.String, nullable = True)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, professor, classid, term, status, readts, writets):
        self.classid = classid
        '''change this later to be date time input by user!!!'''
        self.startTime = datetime.datetime.now()

        # self.lecture = lecture
        self.term = term
        self.status = status
        self.readts = readts
        self.writets = writets

class IClickerReponse(db.Model):
    __tablename__ = 'iclickerresponse'

    reponse = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String, nullable = False)
    sessionid = db.Column(db.Integer, nullable = False)
    questionid = db.Column(db.Integer, nullable = False)
    studentreponse = db.Column(db.String, nullable = True)
    responsetimes = db.Column(db.DateTime, nullable = False)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, netid, sessionid, questionid, studentreponse, readts, writets):
        self.netid = netid
        self.sessionid = sessionid
        self.questionid = questionid
        self.studentreponse = studentreponse
        self.responsetimes = datetime.datetime.now()
        self.readts = readts
        self.writets = writets

class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    registerid = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String, nullable = False)
    classid = db.Column(db.String, nullable = False)
    term = db.Column(db.String, nullable = False)
    registertimes = db.Column(db.DateTime, nullable = False)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, netid, classid, term, readts, writets):
        self.netid = netid
        self.classid = classid
        self.term = term
        self.registertimes = datetime.datetime.now()
        self.readts = readts
        self.writets = writets


class IClickerQuestion(db.Model):
    __tablename__ = 'iclickerquestion'

    iqid = db.Column(db.Integer, primary_key = True)
    ques = db.Column(db.String, nullable = False)
    optiona = db.Column(db.String, nullable = False)
    optionb = db.Column(db.String, nullable = True)
    optionc = db.Column(db.String, nullable = True)
    optiond = db.Column(db.String, nullable = True)
    answer = db.Column(db.String, nullable = False)
    #sessionId number between 1 - 41, total number of lecture in semester
    sessionid = db.Column(db.Integer, nullable = True)
    date_posted = db.Column(db.DateTime, nullable = False)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, ques, answer, optiona, sessionid, optionb, optionc, optiond, readts, writets):
        self.ques = ques
        self.optiona = optiona
        self.optionb = optionb
        self.optionc = optionc
        self.optiond = optiond
        self.answer = answer
        self.sessionid = sessionid
        self.date_posted = datetime.datetime.now()
        self.readts = readts
        self.writets = writets

class QuestionStatus(db.Model):
    __tablename__ = 'questionstatus'

    qstatusid = db.Column(db.Integer, primary_key = True)
    sessionid = db.Column(db.Integer, nullable=True, default=None)
    questionnum = db.Column(db.Integer, nullable=True)
    starttime = db.Column(db.DateTime, nullable = True, default=None)
    endtime = db.Column(db.DateTime, nullable = True, default=None)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, questionnum, sessionid, starttime, endtime, readts, writets):
        self.questionstatuskey = db.Column(db.Integer, primary_key = True)
        self.sessionid = sessionid
        self.questionnum = questionnum
        self.starttime  = starttime
        self.endtime = endtime
        self.readts = readts
        self.writets = writets


class Timestamp(db.Model):
    __tablename__ = 'timestamp'

    nextavailable = db.Column(db.Integer, primary_key = True, default = 0)

    def __init__(self, nextavailable):
        self.nextavailable = nextavailable

class TimestampTest(db.Model):
    __tablename__ = 'timestamptest'

    key = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.String, nullable=True)
    readts = db.Column(db.Integer, nullable=True, default = 0)
    writets = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, key, value, readts, writets):
        self.key = key
        self.value = value
        self.readts = readts
        self.writets = writets
