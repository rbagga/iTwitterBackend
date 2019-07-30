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
re_api = Namespace('Registration Information', description = 'Registration information operations')
en_api = Namespace('Insert i_clicker Questions', description = 'Insert a question operation')
iclkres_api = Namespace('I clicker reponse', description = 'Insert a reponse operation')
q_api = Namespace('student_question', description = 'student question operations')

iq_api = Namespace('instructor_question', description = 'instructor question operations')
lg_api = Namespace('login', description='Authentication')
cu_api = Namespace('create_user', description = 'create/update user information')

#get_question_model = api.model('qid', {'qid': fields.String(description = 'Question ID to get')})
post_question_model = api.model('question', {'question': fields.String, 'sessionid' : fields.String, 'upvotes': fields.Integer})
get_session_model = api.model('session', {'classId': fields.String(description = 'class ID to get'),
                                'term': fields.String(description = 'term to get')})
post_session_model = api.model('professor', {'professor': fields.String,
                                'term': fields.String,
                                'course_number': fields.String,
                                'endsession': fields.Boolean}
                                )
get_enterquestion_model = api.model('iqid', {'QuestionNumber': fields.Integer(description = 'Question number to get')})
post_enterquestion_model = api.model('Question', {'Question': fields.String,
                                'optionA': fields.String,
                                'answer': fields.String,
                                'lecturenumber': fields.Integer
                                }
                                )
get_registration_model = api.model('netid', {'Netid': fields.String(description = 'Registration ID to get')})
post_registration_model = api.model('Registration', {'netid': fields.String, 'classId' : fields.String, 'term': fields.String})
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
                                                                   'answer:': fields.String,
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
    def post(self):
        params = api.payload
        term = params.pop("term")
        course_number = params.pop("course_number")
        endsession = params.pop("endsession")
        while True:
            try:
                ts = startTransaction()
                if not endsession:
                    #create hash for session_id
                    date = datetime.date.now()
                    startTime = str(startTime)
                    hash_key = startTime+term+course_number
                    #change hash function
                    sessionid = hashlib.sha256(hash_key).hexdigest()
                    newSession = text('INSERT INTO session (sessionid, term, course_number, writets) VALUES (:sessionid, :term, :course_number, :ts)')
                    db.engine.execute(newSession, sessionid=sessionid, term=term, course_number=course_number, ts=ts)
                    #pass this sessionid to every otehr table
                    # student_question_sessionid = text('INSERT INTO ')
                    logger.info("got here")
                else:
                    questionInfo = text('SELECT * FROM student_question WHERE sessionid = :sessionid')
                    responses = db.engine.execute(questionInfo, sessionid=sessionid).fetchall()
                    updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    questions = json.dumps([dict(row) for row in responses])
                    purgeQuestions = text('DELETE * FROM student_question WHERE sessionid = :sessionid')
                    db.engine.execute(purgeQuestions, sessionid=sessionid)

                    #post to piazza
                    #piazzaMigration(questions, networkid, netid, passwd)

                    # endTransaction()
                    # return questions
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "Session information has been updated successfully", 200

@en_api.route('/')
class InsertIclickerquestion(Resource):
    @api.expect(get_iclickerquestion_model)
    @api.doc(body=get_iclickerquestion_model)
    def get(self):
        global response
        params = api.payload
        sessionid = params.pop("sessionid")
        while True:
            try:
                ts = startTransaction()
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
                db.engine.execute(check_table_empty, sessionid=sessionid)
                #update the timestamp
                updatets = text('UPDATE iclickerquestion SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if check_table_empty is None:
                    #table is empty
                    iqid = 1
                else:
                    latest_qid = text('SELECT MAX(iqid) FROM iclickerquestion WHERE sessionid = :sessionid')
                    db.engine.execute(latest_qid, sessionid=sessionid)
                    #update the timestamp
                    updatets = text('UPDATE iclickerquestion SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    iqid = latest_qid+1

                startTime = datetime.datetime.now()
                #timelimit is in minutes
                endTime = startTime + datetime.timedelta(minutes=timelimit)
                newQuestion = text('INSERT INTO iclickerquestion (iqid, ques, answer, optiona, optionb, optionc, optiond, sessionid, writets, startTime, endTime) VALUES (:iqid, :ques, :answer, :optiona, :optionb, :optionc, :optiond, :sessionid, :ts, :startTime, :endTime)')
                db.engine.execute(newQuestion, iqid=iqid, ques=ques, answer=answer, optiona=optiona, optionb=optionb, optionc=optionc, optiond=optiond, sessionid=sessionid, ts=ts, startTime=startTime, endTime=endTime)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return "I-Clicker Question information has been updated successfully", 200


@re_api.route('/')
class StudentEnrollment(Resource):
    def get(self):
        global response
        while True:
            try:
                ts = startTransaction()
                updatets = text('UPDATE enrollment SET readts = :ts')
                db.engine.execute(updatets, ts=ts)
                enrollmentInfo = text('SELECT * from enrollment')
                response = db.engine.execute(enrollmentInfo).fetchall()
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])

    @api.expect(post_registration_model)
    @api.doc(body=post_registration_model)
    def post(self):
        params = api.payload
        netid = params.pop("netid")
        classid = params.pop("classId")
        term = params.pop("term")
        while True:
            try:
                ts = startTransaction()
                newQuestion = text('INSERT INTO enrollment (netid, classid, term, writets) VALUES (:netid, :classid, :term, :ts)')
                db.engine.execute(newQuestion, netid=netid, classid=classid, term=term, ts=ts)
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
    def get(self):
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
    def post(self):
        params = api.payload
        netid = params.pop("netid")
        sessionid = params.pop("sessionid")
        response = params.pop("response")
        while True:
            try:
                ts = startTransaction()
                check_table_empty = text('SELECT * FROM iclickerresponse WHERE sessionid = :sessionid')
                db.engine.execute(check_table_empty, sessionid=sessionid)
                #update the timestamp
                updatets = text('UPDATE iclickerresponse SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if check_table_empty is None:
                    #table is empty
                    iqid = 1
                else:
                    latest_qid = text('SELECT MAX(iqid) FROM iclickerresponse WHERE sessionid = :sessionid')
                    db.engine.execute(latest_qid, sessionid=sessionid)
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
                db.engine.execute(check_table_empty, sessionid=sessionid)
                #update the timestamp
                updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                if check_table_empty is None:
                    #table is empty
                    qid = 1
                else:
                    latest_qid = text('SELECT MAX(qid) FROM student_question WHERE sessionid = :sessionid')
                    db.engine.execute(latest_qid, sessionid=sessionid)
                    #update the timestamp
                    updatets = text('UPDATE student_question SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionid)
                    qid = latest_qid+1

                date_posted = datetime.date.now()
                upvotes = 0
                newQuestion = text('INSERT INTO student_question (qid, ques, sessionid, upvotes, date_posted, writets) VALUES (:netid, :ques, :sessionid, :upvotes, :date_posted, :ts)')
                db.engine.execute(newQuestion, qid=qid, ques=ques, sessionid=sessionid, upvotes=upvotes, date_posted=date_posted, ts=ts)
                endTransaction()

            except psycopg2.Error:
                rollBack()
            else:
                break
            return "Student Question has been updated successfully", 200


@q_api.route('/<netid>/<qid>')
class UpvotesPost(Resource):
    @api.expect(put_upvotes_model)
    @api.doc(body=put_upvotes_model)
    def put(self, netid, qid):
        netid_1 = netid
        qid_1 = qid
        #print(netid_1)
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
