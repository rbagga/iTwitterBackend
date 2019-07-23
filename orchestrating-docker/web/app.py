# app.py


from flask import Flask
from flask import request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig

from sqlalchemy import func, select, text

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)


from models import *

count_total_question = -1

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        post = Post(text)
        db.session.add(post)
        db.session.commit()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/question', methods=['GET', 'POST'])
def index2():
    print("INDEX 2")
    if request.method == 'POST':
        question = request.form['question']
        question_post = Question(question)
        db.session.add(question_post)
        db.session.commit()
    questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('question.html', questions = questions)

@app.route('/instrquestion', methods=['GET', 'POST'])
def instrquestion():
    if request.method == 'POST':
        q = request.form['instr_question']
        a =  request.form['optionA']
        b = request.form['optionB']
        c = request.form['optionC']
        d = request.form['optionD']
        ans = request.form['answer']
        instructor_question = InstrQuestion(q, a, b, c, d, ans)
        db.session.add(instructor_question)
        db.session.commit()
    questions = InstrQuestion.order(InstrQuestion.desc()).all()
    return render_template('instrquestion.html', questions = questions )

@app.route('/newuserinfo', methods=['GET', 'POST'])
def Administrator():
    if request.method == 'POST':
        Netid = request.form['NetId']
        FirstName =  request.form['FirstName']
        LastName= request.form['LastName']
        Email = request.form['Email']
        Password = request.form['Password']
        Instructors = Administrators.NetId.query.filter_by(NetId = Netid)
        if len(Instructors) != 0: 
            newuserInfo = Administrators(NetId, FirstName, LastName, Email, Password)
        db.session.add(newuserInfo)
        db.session.commit()
        else: 
            newuserInfo = Students(NetId, FirstName, LastName, Email, Password)
        db.session.add(newuserInfo)
        db.session.commit()
        return redirect('/question', 302)
    return render_template('newuserinfo.html')

@app.route('/newcourse', methods=['GET', 'POST'])
def newclass():
    if request.method == 'POST':
        CRN = request.form['CRN']
        Year = request.form['Year']
        Term =  request.form['Term']
        Course =  request.form['Course']
        newClass = Courses(CRN, Year,Term, Course)
        db.session.add(newClass)
        db.session.commit()
    return render_template('newcourse.html')


@app.route('/login', methods=['GET', 'POST'])
def index3():
    if request.method == 'POST':
        netid = request.form['netid']
        password = request.form['password']

        netid_Instr = Administrators.NetId.filter(NetId = netid)
        net_Stu = Students.NetId.query.filter_by(NetId = netid)

        Password_Instr = Administrators.Password.filter(NetId = netid)
        Password_Stu = Students.Password.filter(NetId = netid)

        validlogin = False ######## need to check this
        if Password == Password_Instr or Password == Password_Stu and (netid == netid_Instr or netid == netid_Stu):
            validlogin = True
        if validlogin:
            return redirect('/question', 302)
    return render_template('login.html')


@app.route('/update_question', methods=['GET', 'POST'])
def update_record():
    if request.method == "POST":
        qid = request.form['qid']
        new_question = request.form['new_question']
        updated_question = Question.query.get(qid)
        updated_question.ques = new_question
        updated_question.date_posted = datetime.datetime.now()
    questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('question.html', questions = questions)

@app.route('/deletequestion', methods=['GET', 'POST'])
def index4():
    if request.method == 'POST':
        qid_to_delete = request.form['qid']
        Question.query.filter_by(qid=qid_to_delete).delete()
        db.session.commit()
    questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('question.html', questions = questions)

@app.route('/searchquestion', methods=['GET', 'POST'])
def index5():
    if request.method == 'POST':
        qid_to_find = request.form['qid']
        question = Question.query.filter_by(qid=qid_to_find)
        questions = question
    else:
        questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('question.html', questions = questions)

#new_stuff added
@app.route('/count_question', methods=['GET', 'POST'])
def count_question():
    if request.method == 'POST':
        question_asked = request.form['question']
        global count_total_question
        query = text('select count(*) from questions where ques = :question')
        # count_total_query = db.session.query(func.count(questions)).filter(and_(questions.ques == question_asked))
        #count_total_query = db.engine.execute('select count(*) from questions where ques = :question', question = question_asked)
        count_total_query = db.engine.execute(query, question = question_asked)
        count_total = count_total_query.fetchall()
        #print(count_total_question)
    questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('count.html', count = count_total[0][0])

        #reference material
'''
my_stats = session.query(company_changes,func.count(distinct(company_changes.id)).label('ChangesCount'))
.filter(company_changes.closed_at > '2018-06-04',company_changes.closed_at < '2018-06-05')
.group_by(company_changes.username)
.group_by(company_changes.company_name)
'''


if __name__ == '__main__':
    app.run()



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
