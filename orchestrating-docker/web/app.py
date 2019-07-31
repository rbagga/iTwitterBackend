# app.py
# import json
from flask import Flask, jsonify, json
from flask import request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api, Namespace, abort, Resource, fields, marshal_with
from config import BaseConfig
from sqlalchemy import func, select, text, exists, and_
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, verify_jwt_in_request, get_jwt_identity, get_jwt_claims
from functools import wraps
import psycopg2
import hashlib

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

import datetime

from models import *
from logger import *

logger = loggerStart()
from transaction import *
from piazza import *


authorizations = {
    'apikey': {
        'type' : 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(app, authorizations=authorizations, security='apikey')


app.config['JWT_SECRET_KEY'] = 'tD2npsUrdzwTmvHIVQ4m6bKNFSyWXgophaj3DOqxg2dEgPvYVpqk3BZKEsdpI1V'
jwt = JWTManager(app)
jwt._set_error_handler_callbacks(api)
#app.config['JWT_ACCESS_TOKEN_EXPIRES']=86400


s_api = Namespace('Session Information', description = 'question session information operations')
re_api = Namespace('Enrollment Information', description = 'Registration information operations')
en_api = Namespace('I-Clicker Questions', description = 'Insert a question operation')
iclkres_api = Namespace('I clicker reponse', description = 'Insert a reponse operation')
q_api = Namespace('Student Questions', description = 'student question operations')
lg_api = Namespace('login', description='Authentication')
cu_api = Namespace('create_user', description = 'create/update user information')

#get_question_model = api.model('qid', {'qid': fields.String(description = 'Question ID to get')})
post_question_model = api.model('question', {'question': fields.String, 'sessionid' : fields.String})
get_session_model = api.model('session', {'classId': fields.String(description = 'class ID to get'),
                                'term': fields.String(description = 'term to get')})
post_session_model = api.model('professor', {'course_number': fields.String,
                                'endsession': fields.Boolean}
                                )
get_enterquestion_model = api.model('iqid', {'QuestionNumber': fields.Integer(description = 'Question number to get')})
post_enterquestion_model = api.model('Question', {'Question': fields.String,
                                'optionA': fields.String,
                                'answer': fields.String,
                                'lecturenumber': fields.Integer
                                }
                                )
get_enrollment_model = api.model('enrollment', {'course_number': fields.String})
post_enrollment_model = api.model('Enrollment', {'course_number' : fields.String})
get_iclickerresponse_model = api.model('get_iclicker_response', {'iqid': fields.Integer(description = 'Question number to get'), 'sessionid':fields.String})
post_iclickerresponse_model = api.model('iClicker_post_responses', {'netid': fields.String,
                                'sessionid': fields.String,
                                'response': fields.String
                                }
                                )
login_model = api.model('login', {
    'netid': fields.String(description='netid', required=True),
    'password': fields.String(description='Password', required=True)
    })
create_user_model = api.model('create_user', {
    'netid': fields.String(description='netid', required=True),
    'firstname': fields.String(description='firstname', required=True),
    'lastname': fields.String(description='lastname', required=True),
    'password': fields.String(description='Password', required=True)
})
put_upvotes_model = api.model('upvotes', {'sessionId': fields.String(description='sessionId', required=True)})
get_iclickerquestion_model = api.model('iclicker_question_get', {'sessionid': fields.String})
post_iclickerquestion_model = api.model('iclicker_question_post', {'sessionid': fields.String,
                                                                   'question': fields.String,
                                                                   'optA': fields.String,
                                                                   'optB': fields.String,
                                                                   'optC': fields.String,
                                                                   'optD': fields.String,
                                                                   'answer': fields.String,
                                                                   'timelimit': fields.Integer
                                                                   })


api.add_namespace(s_api)
api.add_namespace(re_api)
api.add_namespace(en_api)
api.add_namespace(q_api)
api.add_namespace(re_api)
api.add_namespace(iclkres_api)
api.add_namespace(lg_api)
api.add_namespace(cu_api)


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    while True:
        try:
            ts = startTransaction()
            instructor = text('SELECT * FROM faculty WHERE netid=:netid')
            response = db.engine.execute(instructor, netid=identity).fetchone()
            updatets = text('UPDATE faculty SET readts = :ts WHERE netid=:netid')
            db.engine.execute(updatets, ts=ts, netid=identity)
            endTransaction()
        except psycopg2.Error:
            rollBack()
        else:
            break
    if response is None:
        return {'role': 'student'}
    else:
        return {'role': 'instructor'}

def instructor_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] != 'instructor':
            return "Instructors only!", 403
        else:
            return fn(*args, **kwargs)
    return wrapper

def get_term():
    date = datetime.datetime.today()
    year = date.year
    def get_semester(month, day):
        if (month==8 and day>=27) or month>8:
            return "fa"
        if (month==5 and day>=13) or month>5:
            return "su"
        return "sp"
    semester = get_semester(date.month, date.day)
    return str(year)+"-"+semester


@cu_api.route('/')
class createuser(Resource):
    @api.expect(create_user_model)
    @api.doc(body=create_user_model)
    @api.response(200, 'Successful')
    @api.response(401, 'Authentication Failed')
    def post(self):
        params = api.payload
        netid = params.pop("netid")
        firstname = params.pop("firstname")
        lastname = params.pop("lastname")
        password = params.pop("password")

        while True:
            try:
                ts = startTransaction()
                instructor = text('SELECT * FROM faculty WHERE netid=:netid')
                response = db.engine.execute(instructor, netid=netid).fetchone()
                updatets = text('UPDATE faculty SET readts = :ts WHERE netid=:netid')
                db.engine.execute(updatets, ts=ts, netid=netid)

                if response is None:
                    student = text('SELECT * FROM students WHERE netid=:netid')
                    response = db.engine.execute(student, netid=netid).fetchone()
                    updatets = text('UPDATE students SET readts = :ts WHERE netid=:netid')
                    db.engine.execute(updatets, ts=ts, netid=netid)

                    if response is None:
                        if not piazzaLogin(netid, password):
                            endTransaction()
                            abort(401, 'Authentication Failed: Unknown User')
                        newStudent = text('INSERT INTO students (netid, firstname, lastname, writets) VALUES (:netid, :firstname, :lastname, :ts)')
                        db.engine.execute(newStudent, netid=netid, firstname=firstname, lastname=lastname, ts=ts)
                    else:
                        if not piazzaLogin(netid, password):
                            endTransaction()
                            abort(401, 'Authentication Failed: Student: Please use your Piazza login credentials')
                        updateStudent = text('UPDATE students SET firstname=:firstname, lastname=:lastname, writets=:ts WHERE netid=:netid')
                        db.engine.execute(updateStudent, netid=netid, firstname=firstname, lastname=lastname, ts=ts)
                else:
                    if not piazzaLogin(netid, password):
                        endTransaction()
                        abort(401, 'Authentication Failed: Professor: Please use your Piazza login credentials')
                    updateInstructor = text('UPDATE faculty SET firstname=:firstname, lastname=:lastname, writets=:ts WHERE netid=:netid')
                    db.engine.execute(updateInstructor, netid=netid, firstname=firstname, lastname=lastname, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "User information has been updated successfully", 200

@lg_api.route('/')
class login(Resource):
    @api.expect(login_model)
    @api.doc(body=login_model)
    @api.response(200, 'Login Successful')
    @api.response(401, 'Login Failed')
    def post(self):
        params = api.payload
        netid = params.pop("netid")
        password = params.pop("password")

        while True:
            try:
                ts = startTransaction()
                instructor = text('SELECT * FROM faculty WHERE netid=:netid')
                response = db.engine.execute(instructor, netid=netid).fetchone()
                updatets = text('UPDATE faculty SET readts = :ts WHERE netid=:netid')
                db.engine.execute(updatets, ts=ts, netid=netid)

                if response is None:
                    student = text('SELECT * FROM students WHERE netid=:netid')
                    response = db.engine.execute(student, netid=netid).fetchone()
                    updatets = text('UPDATE students SET readts = :ts WHERE netid=:netid')
                    db.engine.execute(updatets, ts=ts, netid=netid)
                    if response is None:
                        endTransaction()
                        abort(401, 'Login Failed: Unknown User')
                    else:
                        if not piazzaLogin(netid, password):
                            endTransaction()
                            abort(401, 'Login Failed: Student: Please use your Piazza login credentials')
                        # enter student's piazza login info if they are picked by any of their courses
                        enterPiazza = text('UPDATE courses SET piazza_passwd=:passwd, writets=:ts WHERE piazza_netid=:netid')
                        response = db.engine.execute(enterPiazza, passwd=password, ts=ts, netid=netid)
                else:
                    if not piazzaLogin(netid, password):
                        endTransaction()
                        abort(401, 'Login Failed: Professor: Please use your Piazza login credentials')
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        token = create_access_token(identity=netid)
        return {'token': token}, 200

@s_api.route('/')
class sessioninformation(Resource):
    @jwt_required
    def get(self):
        global response
        while True:
            try:
                ts = startTransaction()
                sessionInfo = text('SELECT * from session')
                response = db.engine.execute(sessionInfo).fetchall()
                updatets = text('UPDATE session SET readts = :ts')
                db.engine.execute(updatets, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])

    @api.expect(post_session_model)
    @api.doc(body=post_session_model)
    #@instructor_required
    def post(self):
        params = api.payload
        term = get_term()
        course_number = params.pop("course_number")  # change this to be gotten from table
        endsession = params.pop("endsession")
        while True:
            try:
                ts = startTransaction()
                date_key = str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)
                hash_key = date_key+term+course_number
                sessionid = hashlib.sha256(hash_key.encode('utf-8')).hexdigest()
                if not endsession:
                    checkSession = text('SELECT * FROM session WHERE sessionid=:sessionid')
                    sameSession = db.engine.execute(checkSession, sessionid=sessionid).fetchone()
                    updatets = text('UPDATE session SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)

                    if sameSession is None:
                        newSession = text('INSERT INTO session (sessionid, date, term, course_number, writets) VALUES (:sessionid, :date, :term, :course_number, :ts)')
                        db.engine.execute(newSession, sessionid=sessionid, date=date_key, term=term, course_number=course_number, ts=ts)
                    #pass this sessionid to every otehr table
                    # student_question_sessionid = text('INSERT INTO ')
                else:
                    # post to piazza, then delete questions
                    questionInfo = text('SELECT ques FROM student_question WHERE sessionid = :sessionid')
                    questions = db.engine.execute(questionInfo, sessionid=sessionid).fetchall()
                    updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)

                    # get networkid, netid and password of a student
                    courseInfo = text('SELECT piazza_nid, piazza_netid, piazza_passwd FROM courses WHERE course_number=:course_number AND term=:term')
                    piazzaTuple = db.engine.execute(courseInfo, course_number=course_number, term=term).fetchone()
                    piazza_nid, piazza_netid, piazza_passwd = piazzaTuple[0], piazzaTuple[1], piazzaTuple[2]
                    updatets = text('UPDATE courses SET readts = :ts WHERE course_number = :course_number AND term = :term')
                    db.engine.execute(updatets, ts=ts, course_number=course_number, term=term)

                    piazzaMigration(questions, piazza_nid, piazza_netid, piazza_passwd)

                    # Purge everything
                    purgeQuestions = text('DELETE FROM student_question WHERE sessionid = :sessionid')
                    db.engine.execute(purgeQuestions, sessionid=sessionid)
                    # then delete session information?
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "Session information has been updated successfully", 200

@en_api.route('/')
class Iclickerquestion(Resource):
    @jwt_required
    def get(self):
        global response
        netid = get_jwt_identity()
        while True:
            try:
                ts = startTransaction()
                sessionid_query = text('SELECT session.sessionid FROM session JOIN enrollment ON session.course_number = enrollment.course_number AND session.term = enrollment.term WHERE enrollment.netid = :netid')
                sessionid_list = db.engine.execute(sessionid_query, netid=netid).fetchone()
                if sessionid_list is not None:
                    sessionid = sessionid_list[0]
                    updatets = text('UPDATE enrollment SET readts = :ts WHERE netid = :netid')
                    db.engine.execute(updatets, ts=ts, netid=netid)
                    updatets2 = text('UPDATE session SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets2, ts=ts, sessionid=sessionid)
                    questionInfo = text('SELECT ques FROM iclickerquestion WHERE sessionid = :sessionid')
                    response = db.engine.execute(questionInfo, sessionid=sessionid).fetchall()
                    updatets = text('UPDATE iclickerquestion SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return jsonify({'response' : [dict(row) for row in response]})

    @api.expect(post_iclickerquestion_model)
    @api.doc(body=post_iclickerquestion_model)
    #@instructor_required
    def post(self):
        params = api.payload
        ques = params.pop("question")
        optiona = params.pop("optA")
        optionb = params.pop("optB")
        optionc = params.pop("optC")
        optiond = params.pop("optD")
        answer = params.pop("answer")
        sessionid = params.pop("sessionid")
        timelimit = params.pop("timelimit")
        while True:
            try:
                ts = startTransaction()
                #check if table si empty or not for iqid
                check_table_empty = text('SELECT * FROM iclickerquestion WHERE sessionid = :sessionid')
                table_entries = db.engine.execute(check_table_empty, sessionid=sessionid).fetchone()
                #update the timestamp
                updatets = text('UPDATE iclickerquestion SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if table_entries is None:
                    #table is empty
                    iqid = 1
                else:
                    get_latest_qid = text('SELECT MAX(iqid) FROM iclickerquestion WHERE sessionid = :sessionid')
                    latest_qid = db.engine.execute(get_latest_qid, sessionid=sessionid).scalar()
                    #update the timestamp
                    updatets = text('UPDATE iclickerquestion SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    iqid = latest_qid+1

                starttime = datetime.datetime.now()
                #timelimit is in minutes
                endtime = starttime + datetime.timedelta(minutes=timelimit)
                newQuestion = text('INSERT INTO iclickerquestion (iqid, ques, answer, optiona, optionb, optionc, optiond, sessionid, writets, starttime, endtime) VALUES (:iqid, :ques, :answer, :optiona, :optionb, :optionc, :optiond, :sessionid, :ts, :starttime, :endtime)')
                db.engine.execute(newQuestion, iqid=iqid, ques=ques, answer=answer, optiona=optiona, optionb=optionb, optionc=optionc, optiond=optiond, sessionid=sessionid, ts=ts, starttime=starttime, endtime=endtime)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "I-Clicker Question information has been updated successfully", 200


@re_api.route('/')
class StudentEnrollment(Resource):
    @jwt_required
    def get(self):
        netid = get_jwt_identity()
        global response
        while True:
            try:
                ts = startTransaction()
                enrollmentInfo = text('SELECT * FROM enrollment WHERE netid=:netid')
                response = db.engine.execute(enrollmentInfo, netid=netid).fetchall()
                updatets = text('UPDATE enrollment SET readts = :ts WHERE netid=:netid')
                db.engine.execute(updatets, ts=ts, netid=netid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])

    @api.expect(post_enrollment_model)
    @api.doc(body=post_enrollment_model)
    @jwt_required
    def post(self):
        params = api.payload
        netid = get_jwt_identity()
        course_number = params.pop("course_number")
        term = get_term()
        while True:
            try:
                ts = startTransaction()

                checkEnrollment = text('SELECT * FROM enrollment WHERE netid=:netid AND course_number=:course_number AND term=:term')
                alreadyEnrolled = db.engine.execute(checkEnrollment, netid=netid, course_number=course_number, term=term).fetchone()
                updatets = text('UPDATE enrollment SET readts = :ts WHERE netid=:netid AND course_number=:course_number AND term=:term')
                db.engine.execute(updatets, ts=ts, netid=netid, course_number=course_number, term=term)

                if alreadyEnrolled is None:
                    newEnrollment = text('INSERT INTO enrollment (netid, course_number, term, writets) VALUES (:netid, :course_number, :term, :ts)')
                    db.engine.execute(newEnrollment, netid=netid, course_number=course_number, term=term, ts=ts)
                # Sets piazza netid for this course only if it is null
                updatePiazzaNetid = text('UPDATE courses SET piazza_netid=:netid, writets=:ts WHERE course_number=:course_number AND term=:term AND piazza_netid IS NULL')
                db.engine.execute(updatePiazzaNetid, netid=netid, ts=ts, course_number=course_number, term=term)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "Enrollment information has been updated successfully", 200

@iclkres_api.route('/')
class Iclickerresponse(Resource):
    @api.expect(get_iclickerresponse_model)
    @api.doc(body=get_iclickerresponse_model)
    @jwt_required
    def get(self):  ###why do we have this?
        global response
        params = api.payload
        iqid = params.pop("iqid")
        sessionid = params.pop("sessionid")
        # netid = params.pop("netid")
        while True:
            try:
                ts = startTransaction()
                iclickerresponseInfo = text('SELECT * from iclickerresponse WHERE sessionid = :sessionid AND iqid = :iqid')
                response = db.engine.execute(iclickerresponseInfo, sessionid=sessionid, iqid=iqid).fetchall()
                updatets = text('UPDATE iclickerresponse SET readts = :ts WHERE sessionid = :sessionid AND iqid = :iqid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid, iqid=iqid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])

    @api.expect(post_iclickerresponse_model)
    @api.doc(body=post_iclickerresponse_model)
    @jwt_required
    def post(self):
        params = api.payload
        netid = get_jwt_identity()
        sessionid = params.pop("sessionid")
        response = params.pop("response")
        while True:
            try:
                ts = startTransaction()
                check_table_empty = text('SELECT * FROM iclickerresponse WHERE sessionid = :sessionid')
                table_entries = db.engine.execute(check_table_empty, sessionid=sessionid).fetchone()
                #update the timestamp
                updatets = text('UPDATE iclickerresponse SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if table_entries is None:
                    #table is empty
                    iqid = 1
                else:
                    get_latest_qid = text('SELECT MAX(iqid) FROM iclickerresponse WHERE sessionid = :sessionid')
                    latest_qid = db.engine.execute(latest_qid, sessionid=sessionid).scalar()
                    #update the timestamp
                    updatets = text('UPDATE iclickerresponse SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    iqid = latest_qid+1

                responsetime = datetime.datetime.now()
                newQuestion = text('INSERT INTO iclickerresponse (netid, sessionid, response, iqid, responsetime, writets) VALUES (:netid, :sessionid, :response, :iqid, :responsetime, :ts)')
                db.engine.execute(newQuestion, netid=netid, sessionid=sessionid, response=response, iqid=iqid, responsetime=responsetime, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "I-Clicker Response information has been updated successfully", 200


@q_api.route('/')
class StudentQuestionPost(Resource):
    @jwt_required
    def get(self):
        global response
        while True:
            try:
                ts = startTransaction()
                questionInfo = text('SELECT * from student_question')
                response = db.engine.execute(questionInfo).fetchall()
                updatets = text('UPDATE student_question SET readts = :ts')
                db.engine.execute(updatets, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])
    @api.expect(post_question_model)
    @api.doc(body=post_question_model)
    @jwt_required
    def post(self):
        params = api.payload
        ques = params.pop("question")
        # netid = params.pop("netid")
        #get session_id from session
        sessionid = params.pop("sessionid")

        while True:
            try:
                ts = startTransaction()
                check_table_empty = text('SELECT * FROM student_question WHERE sessionid = :sessionid')
                table_entries = db.engine.execute(check_table_empty, sessionid=sessionid).fetchone()
                #update the timestamp
                updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if table_entries is None:
                    #table is empty
                    qid = 1
                else:
                    get_latest_qid = text('SELECT MAX(qid) FROM student_question WHERE sessionid = :sessionid')
                    latest_qid = db.engine.execute(get_latest_qid, sessionid=sessionid).scalar()
                    #update the timestamp
                    updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    qid = latest_qid+1

                date_posted = datetime.datetime.now()
                newQuestion = text('INSERT INTO student_question (qid, ques, sessionid, upvotes, date_posted, writets) VALUES (:qid, :ques, :sessionid, :upvotes, :date_posted, :ts)')
                db.engine.execute(newQuestion, qid=qid, ques=ques, sessionid=sessionid, upvotes=0, date_posted=date_posted, ts=ts)
                endTransaction()

            except psycopg2.Error:
                rollBack()
            else:
                break
            return "Student Question has been updated successfully", 200


@q_api.route('/<qid>')
class UpvotesPost(Resource):
    @api.expect(put_upvotes_model)
    @api.doc(body=put_upvotes_model)
    @jwt_required
    def put(self, qid):
        netid = get_jwt_identity()
        qid = qid
        params = api.payload
        sessionid = params.pop('sessionId')
        while True:
            try:
                ts = startTransaction()

                votesInfo = text('SELECT upvotes FROM student_question WHERE qid = :qid AND sessionid = :sessionid')
                response = db.engine.execute(votesInfo, qid=qid, sessionid=sessionid).scalar()
                updatets = text('UPDATE student_question SET readts = :ts WHERE qid = :qid AND sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, qid=qid, sessionid=sessionid)
                new_votes = 0
                exists_query = text('SELECT netid FROM upvotes WHERE EXISTS (SELECT netid FROM upvotes WHERE netid = :netid AND qid = :qid AND sessionid = :sessionid)')
                existing = db.engine.execute(exists_query, netid = netid, qid = qid, sessionid=sessionid).fetchall()
                updatets = text('UPDATE upvotes SET readts = :ts WHERE EXISTS (SELECT netid FROM upvotes WHERE netid = :netid AND qid = :qid AND sessionid = :sessionid)')
                db.engine.execute(updatets, ts=ts, netid=netid, qid=qid, sessionid=sessionid)
                already_upvoted = (len(existing) > 0)
                if (not already_upvoted):
                    new_votes = response + 1
                    newUpvote = text('INSERT INTO upvotes (netid, qid, sessionid, writets) VALUES (:netid, :qid, :sessionid, :ts)')
                    db.engine.execute(newUpvote, netid=netid, qid=qid, sessionid=sessionid, ts=ts)
                else:
                    new_votes = response - 1
                    deleteUpvote = text('DELETE FROM upvotes WHERE netid = :netid AND qid = :qid AND sessionid = :sessionid')
                    db.engine.execute(deleteUpvote, netid = netid, qid=qid, sessionid=sessionid)

                update_query = text('UPDATE student_question SET upvotes = :upvotes, writets=:ts  WHERE qid=:qid AND sessionid=:sessionid')
                db.engine.execute(update_query, upvotes = new_votes, ts=ts, qid = qid, sessionid=sessionid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break

if __name__ == '__main__':
    app.run(debug=True)
