import requests
from flask import Blueprint, render_template, request, jsonify, session
from app.models import Result, Category, db
from random import shuffle
import time

quiz_bp = Blueprint('quiz', __name__)

OPENTDB_API_URL = "https://opentdb.com/api.php"

@quiz_bp.route('/')
def home():
    return render_template('index.html')
    #return jsonify({'categories': [{'id': c.id, 'name': c.name} for c in categories]}), 200

@quiz_bp.route('/categories', methods=['GET'])
def get_categories():
    response = requests.get("https://opentdb.com/api_category.php")
    if response.status_code == 200:
        categories = response.json().get('trivia_categories', [])
        return jsonify(categories)
    return jsonify({'error': 'Failed to fetch categories'}), 500

@quiz_bp.route('/questions', methods=['GET'])
def get_questions():
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty', default='easy', type=str)
    amount = request.args.get('amount', default=10, type=int)

    if not category_id:
        return jsonify({'error': 'Category ID is required'}), 400

    params = {
        'amount': amount,
        'category': category_id,
        'difficulty': difficulty,
        'type': 'multiple',
    }

    response = requests.get(OPENTDB_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['response_code'] == 0:
            questions = []
            for question in data['results']:
                # Combine correct and incorrect answers
                options = question['incorrect_answers']
                options.append(question['correct_answer'])
                # Shuffle options for fairness
                shuffle(options)

                questions.append({
                    'id': question.get('question'),  # Use the question text as ID (temporary)
                    'question_text': question.get('question'),
                    'correct_answer': question.get('correct_answer'),
                    'options': options,
                })
            return jsonify(questions)
        else:
            return jsonify({'error': 'No questions found'}), 404

    return jsonify({'error': 'Failed to fetch questions'}), 500

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    answers = data['answers']
    score = 0
    total_questions = len(answers)

    for answer in answers:
        if answer['selected_option'] == answer['correct_answer']:
            score += 1

    result = Result(user_id=session['user_id'], score=score, total_questions=total_questions)
    db.session.add(result)
    db.session.commit()

    return jsonify({'score': score, 'total_questions': total_questions}), 200

quiz_bp.route('/results', methods=['GET'])
def get_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    results = Result.query.filter_by(user_id=user_id).all()
    return jsonify([
        {'score': r.score, 'total_questions': r.total_questions} for r in results
    ])

@quiz_bp.route('/timer', methods=['GET'])
def timer():
    start_time = time.time()
    duration = request.args.get('duration', default=30, type=int)
    return jsonify({'start_time': start_time, 'duration': duration}), 200