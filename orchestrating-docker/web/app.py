# app.py


from flask import Flask
from flask import request, render_template, redirect
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

@app.route('/login', methods=['GET', 'POST'])
def index3():
    if request.method == 'POST':
        netid = request.form['netid']
        password = request.form['password']
        validlogin = True ######## need to check this
        if validlogin:
            return redirect('/question', 302)
    return render_template('login.html')



if __name__ == '__main__':
    app.run()
