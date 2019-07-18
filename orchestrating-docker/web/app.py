# app.py


from flask import Flask
from flask import request, render_template
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig


app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)


from models import *


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

@app.route('/update_question', methods=['GET', 'POST'])
def update_record():
    if request.method == "POST":
        qid = request.form['qid']
        new_question = request.form['new_question']
        updated_question = Question.query.get(qid)
        updated_question.ques = new_question
        updated_question.date_posted = datetime.datetime.now()
        db.session.commit()
    questions = Question.query.order_by(Question.date_posted.desc()).all()
    return render_template('question.html', questions = questions)

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
