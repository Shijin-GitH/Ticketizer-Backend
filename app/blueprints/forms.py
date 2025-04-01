from flask import Blueprint, jsonify, request
from app.models import Ticket, Event, User, FormQuestion, FormAnswer
from functools import wraps
import jwt
from flask import current_app
from app import db

bp = Blueprint('forms', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(User_id=data['user_id']).first()
        except:
            return jsonify({'error': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/<string:event_token>/form_questions', methods=['POST'])
@token_required
def add_form_question(current_user, event_token):
    data = request.json
    event = Event.query.filter_by(token=event_token).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    question = FormQuestion(
        event_id=event.event_id,
        question_type=data['question_type'],
        question=data['question'],
        options=data.get('options')
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'message': 'Form question added successfully!', 'question_id': question.question_id}), 201

@bp.route('/form_questions/<int:question_id>', methods=['PUT'])
@token_required
def edit_form_question(current_user, question_id):
    data = request.json
    question = FormQuestion.query.get_or_404(question_id)
    question.question_type = data.get('question_type', question.question_type)
    question.question = data.get('question', question.question)
    question.options = data.get('options', question.options)
    db.session.commit()
    return jsonify({'message': 'Form question updated successfully!'})

@bp.route('/form_questions/<int:question_id>', methods=['DELETE'])
@token_required
def delete_form_question(current_user, question_id):
    question = FormQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Form question deleted successfully!'})

@bp.route('/<string:event_token>/form_questions', methods=['GET'])
@token_required
def view_all_form_questions(current_user, event_token):
    event = Event.query.filter_by(token=event_token).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    questions = FormQuestion.query.filter_by(event_id=event.event_id).all()
    return jsonify([{
        'question_id': q.question_id,
        'event_id': q.event_id,
        'question_type': q.question_type,
        'question': q.question,
        'options': q.options
    } for q in questions])

@bp.route('/form_answers', methods=['POST'])
@token_required
def add_form_answer(current_user):
    data = request.json
    answer = FormAnswer(
        question_id=data['question_id'],
        answer=data['answer']
    )
    db.session.add(answer)
    db.session.commit()
    return jsonify({'message': 'Form answer added successfully!', 'answer_id': answer.answer_id}), 201

@bp.route('/form_answers/<int:answer_id>', methods=['PUT'])
@token_required
def edit_form_answer(current_user, answer_id):
    data = request.json
    answer = FormAnswer.query.get_or_404(answer_id)
    answer.answer = data.get('answer', answer.answer)
    db.session.commit()
    return jsonify({'message': 'Form answer updated successfully!'})

@bp.route('/form_answers/<int:answer_id>', methods=['DELETE'])
@token_required
def delete_form_answer(current_user, answer_id):
    answer = FormAnswer.query.get_or_404(answer_id)
    db.session.delete(answer)
    db.session.commit()
    return jsonify({'message': 'Form answer deleted successfully!'})

# @bp.route('/form_answers', methods=['GET'])
# @token_required
# def view_all_form_answers(current_user):
#     question_id = request.args.get('question_id')
#     answers = FormAnswer.query.filter_by(question_id=question_id).all()
#     return jsonify([{
#         'answer_id': a.answer_id,
#         'question_id': a.question_id,
#         'answer': a.answer
#     } for a in answers])
