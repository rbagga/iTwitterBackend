from flask import jsonify
from flask_restplus import Namespace, abort, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,select, text
# from app import Question

api = Namespace('question', description = 'question operations')


@api.route('/question/<qid>')
class StudentQuestions(Resource):
    # @api.marshal_list_with(get_question_model)
    # @api.expect(get_question_model, validate=True)
	# from models import Question
    def get(self, qid):
        x = models.Question(3)
        # return jsonify(posts=list(Question.query.all()))
        return True
    # Question.query.filter_by(qid=qid).all())
    # def post(self, question):
    #     question_post = Question(question)
    #     db.session.add(question_post)
    #     db.session.commit()
    #     return True
