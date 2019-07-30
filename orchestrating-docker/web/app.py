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
en_api = Namespace('Insert Questions', description = 'Insert a question operation')
iclkres_api = Namespace('I clicker reponse', description = 'Insert a reponse operation')
q_api = Namespace('student_question', description = 'student question operations')
iq_api = Namespace('instructor_question', description = 'instructor question operations')
lg_api = Namespace('login', description='Authentication')
cu_api = Namespace('create_user', description = 'create/update user information')

#get_question_model = api.model('qid', {'qid': fields.String(description = 'Question ID to get')})
post_question_model = api.model('question', {'question': fields.String, 'netid': fields.String, 'sessionid' : fields.Integer, 'upvotes': fields.Integer})
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
get_iclickerreponse_model = api.model('reponse', {'Response Number': fields.Integer(description = 'Question number to get')})
post_iclickerreponse_model = api.model('Response', {'Netid': fields.String,
                                'sessionId': fields.Integer,
                                'questionnum': fields.Integer,
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
                    newSession = text('INSERT INTO session (sessionid, term, course_number, writets) VALUES (:sessionid, :term, :classid, :ts)')
                    db.engine.execute(newSession, sessionid=sessionid, term=term, course_number=course_number, ts=ts)
                    #pass this sessionid to every otehr table
                    student_question_sessionid = text('INSERT INTO ')
                    logger.info("got here")
                else:
                    # post to piazza, then delete questions

                    questionInfo = text('SELECT * from questions WHERE sessionid = :sessionid')
                    responses = db.engine.execute(questionInfo, sessionid=sessionid).fetchall()
                    updatets = text('UPDATE questions SET readts = :ts WHERE sessionid = :sessionid')
                    db.engine.execute(updatets, ts=ts, sessionid=sessionied)
                    questions = json.dumps([dict(row) for row in responses])



                    #piazzaMigration(questions, networkid, netid, passwd)

                    endTransaction()
                    return questions



                    # then delete session information?
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break

        return "Session information has been updated successfully", 200

@en_api.route('/')
class Insertquestion(Resource):
    def get(self):
        global response
        while True:
            try:
                ts = startTransaction()
                questionInfo = text('SELECT ques from iclickerquestion')
                response = db.engine.execute(questionInfo).fetchall()
                updatets = text('UPDATE iclickerquestion SET readts = :ts')
                db.engine.execute(updatets, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return jsonify({'response' : [dict(row) for row in response]})

    @api.expect(post_enterquestion_model)
    @api.doc(body=post_enterquestion_model)
    def post(self):
        params = api.payload
        ques = params.pop("Question")
        optiona = params.pop("optionA")
        answer = params.pop("answer")
        sessionid = params.pop("lecturenumber")
        while True:
            try:
                ts = startTransaction()
                newQuestion = text('INSERT INTO iclickerquestion (ques, answer, optiona, sessionid, writets) VALUES (:ques, :answer, :optiona, :sessionid, :ts)')
                db.engine.execute(newQuestion, ques=ques, answer=answer, optiona=optiona, sessionid=sessionid, ts=ts)
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
class Iclickerreponse(Resource):
    def get(self):
        global response
        while True:
            try:
                ts = startTransaction()
                iclickerresponseInfo = text('SELECT * from iclickerresponse')
                response = db.engine.execute(iclickerresponseInfo).fetchall()
                updatets = text('UPDATE iclickerresponse SET readts = :ts')
                db.engine.execute(updatets, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])

    @api.expect(post_iclickerreponse_model)
    @api.doc(body=post_iclickerreponse_model)
    def post(self):
        params = api.payload
        netid = params.pop("Netid")
        sessionid = params.pop("sessionId")
        questionid = params.pop("questionnum")
        studentreponse = params.pop("response")
        while True:
            try:
                ts = startTransaction()
                newQuestion = text('INSERT INTO iclickerresponse (netid, sessionid, questionid, studentresponse, writets) VALUES (:netid, :sessionid, :questionid, :studentresponse, :ts)')
                db.engine.execute(newQuestion, netid=netid, sessionid=sessionid, questionid=questionid, studentresponse=studentresponse, ts=ts)
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
                questionInfo = text('SELECT * from questions')
                response = db.engine.execute(questionInfo).fetchall()
                updatets = text('UPDATE questions SET readts = :ts')
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
        netid = params.pop("netid")
        sessionid = params.pop("sessionid")

        while True:
            try:
                ts = startTransaction()
                newQuestion = text('INSERT INTO questions (ques, netid, sessionid, writets) VALUES (:netid, :ques, :sessionid, :ts)')
                db.engine.execute(newQuestion, ques=ques, netid=netid, sessionid=sessionid, ts=ts)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
            return "Student Question has been updated successfully", 200


@q_api.route('/<netid>/<qid>')
class UpvotesPost(Resource):
    def put(self, netid, qid):
        netid_1 = netid
        qid_1 = qid
        #print(netid_1)
        while True:
            try:
                ts = startTransaction()

                votesInfo = text('SELECT upvotes FROM questions WHERE qid = :qid')
                response = db.engine.execute(votesInfo, qid=qid).scalar()
                updatets = text('UPDATE questions SET readts = :ts WHERE qid = :qid')
                db.engine.execute(updatets, ts=ts, qid=qid)
                new_votes = 0
                exists_query = text('SELECT netid FROM upvotes WHERE EXISTS (SELECT netid FROM upvotes WHERE netid = :netid AND qid = :qid)')
                existing = db.engine.execute(exists_query, netid = netid, qid = qid).fetchall()
                updatets = text('UPDATE upvotes SET readts = :ts WHERE EXISTS (SELECT netid FROM upvotes WHERE netid = :netid AND qid = :qid)')
                db.engine.execute(updatets, ts=ts, netid=netid, qid=qid)
                already_upvoted = (len(existing) > 0)
                if (not already_upvoted):
                    new_votes = response + 1
                    newUpvote = text('INSERT INTO upvotes (netid, qid) VALUES (:netid, qid, :ts)')
                    db.engine.execute(newUpvote, netid=netid, qid=qid, ts=ts)
                else:
                    new_votes = response - 1
                    deleteUpvote = text('DELETE FROM upvotes WHERE netid = :netid')
                    db.engine.execute(deleteUpvote, netid = netid)
                update_query = text('UPDATE questions SET upvotes = :upvotes, writets=:ts  WHERE qid=:qid')
                db.engine.execute(update_query, upvotes = new_votes, ts=ts, qid = qid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break


@q_api.route('/<qid>')
class StudentQuestion(Resource):
    def get(self, qid):
        global response
        while True:
            try:
                ts = startTransaction()
                questionInfo = text('SELECT * from questions WHERE qid = :questionid')
                response = db.engine.execute(questionInfo, questionid=qid).fetchall()
                updatets = text('UPDATE questions SET readts = :ts WHERE qid = :questionid')
                db.engine.execute(updatets, ts=ts, questionid=qid)
                endTransaction()
            except psycopg2.Error:
                rollBack()
            else:
                break
        return json.dumps([dict(row) for row in response])


@api.route('/question/<qid>')
class StudentQuestions(Resource):
    # @api.marshal_list_with(get_question_model)
    # @api.expect(get_question_model, validate=True)
    def get(self, qid):
        return True
    # def post(self, question):
    #     question_post = Question(question)
    #     db.session.add(question_post)
    #     db.session.commit()
    #     return True

        #reference material
'''
my_stats = session.query(company_changes,func.count(distinct(company_changes.id)).label('ChangesCount'))
.filter(company_changes.closed_at > '2018-06-04',company_changes.closed_at < '2018-06-05')
.group_by(company_changes.username)
.group_by(company_changes.company_name)
'''


if __name__ == '__main__':
    app.run(debug=True)



#Reference Material: Delete after use
'''
@app.route('/edit/<int:id>', methods=["POST", "GET"])
    def update_record(id):
        if request.method == "POST":
            flight = request.form["flight"]
            destination = request.form["destination"]
            check_in = datetime.strptime(request.form['check_in'], '%d-%m-%Y %H:%M %p')
            depature = datetime.strptime(request.form['depature'], '%d-%m-%Y %H:%M %p')
            status = request.form["status"]

            update_flight = Flight.query.get(id)
            update_flight.flight = flight
            update_flight.destination = destination
            update_flight.check_in = check_in
            update_flight.depature = depature
            update_flight.status = status
            db_session.commit()

            return redirect("/backend", code=302)
        else:
            new_flight = Flight.query.get(id)
            new_flight.check_in = new_flight.check_in.strftime("%d-%m-%Y %H:%M %p")
            new_flight.depature = new_flight.depature.strftime("%d-%m-%Y %H:%M %p")

            return render_template('update_flight.html', data=new_flight)
'''
