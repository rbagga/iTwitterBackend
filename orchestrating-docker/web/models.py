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

class Courses(db.Model):
    __tablename__ = 'NewCoursesInfo'

    CRN = db.Column(db.Integer, primary_key = True)
    Year = db.Column(db.Integer, nullable = True)
    Term = db.Column(db.String, nullable = True)
    Course = db.Column(db.String, nullable = True)
    
    def __init__(self, CRN, Year, Term, Course):
        self.CRN = CRN
        self.Year = Year
        self.Term = Term
        self.Course = Course

class login_Info(db.Model):
    __tablename__ = 'LoginInfo'

    NetId = db.Column(db.String, primary_key = True)
    Password = db.Column(db.String, nullable = True)

    def __init__(self, NetId, Password):
        self.NetId = NetId
        self.Password = Password

class Students(db.Model):
    __tablename__ = 'Students'

    NetId = db.Column(db.String, primary_key = True)
    FirstName = db.Column(db.String, nullable = True)
    LastName = db.Column(db.String, nullable = True)
    Email = db.Column(db.String, nullable = True)
    UIN = db.Column(db.Integer, nullable = False)
    
    def __init__(self, NetId, FirstName, LastName, Email):
        self.NetId = NetId
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email

class Administrators(db.Model):
    __tablename__ = 'Administrator'

    NetId = db.Column(db.String, primary_key = True)
    FirstName = db.Column(db.String, nullable = True)
    LastName = db.Column(db.String, nullable = True)
    Email = db.Column(db.String, nullable = True)
    UIN = db.Column(db.Integer, nullable = False)
    
    def __init__(self, NetId, FirstName, LastName, Email):
        self.NetId = NetId
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        