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

    questions = InstrQuestion.query.order_by(InstrQuestion.date_posted.desc()).all()
    return render_template('instrquestion.html', questions = questions )
if __name__ == '__main__':
    app.run()
