from flask import Blueprint, request, jsonify
from .models import ExampleModel
from . import db

bp = Blueprint('main', __name__)

@bp.route('/example', methods=['GET'])
def get_example():
    examples = ExampleModel.query.all()
    return jsonify([example.name for example in examples])

@bp.route('/example', methods=['POST'])
def add_example():
    data = request.get_json()
    new_example = ExampleModel(name=data['name'])
    db.session.add(new_example)
    db.session.commit()
    return jsonify({'message': 'Example added!'}), 201
