from flask import Blueprint, render_template, request, jsonify, session
from app.models import Category, Question, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def check_admin():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized access'}), 403
    
@admin_bp.route('/dashboard')
def admin_dashboard():
    categories = Category.query.all()
    return render_template('admin_dashboard.html', categories=categories)

@admin_bp.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name')
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category added successfully!'})

@admin_bp.route('/add_question', methods=['POST'])
def add_question():
    category_id = request.form.get('category_id')
    question_text = request.form.get('question_text')
    correct_answer = request.form.get('correct_answer')
    options = request.form.getlist('options')
    new_question = Question(
        category_id=category_id,
        question_text=question_text,
        correct_answer=correct_answer,
        options=options
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added successfully!'})