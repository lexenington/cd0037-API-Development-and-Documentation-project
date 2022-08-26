import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginated_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    return questions[start:end]

def categories():
    return Category.query.order_by(Category.id).all()

    

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r'/api/*': {'origins':'*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPOTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        category_list = categories()

        if len(category_list) == 0:
            abort(404)

        category_dict = {cat.id: cat.type for cat in category_list}
        return jsonify({
            'success': True,
            'categories': category_dict})


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        questions_list = Question.query.order_by(Question.id).all()
        requested_qustions = paginated_questions(request, questions_list)
        
        categories_list = categories()
        categories_dict = {cat.id: cat.type for cat in categories_list}
        
        if len(requested_qustions) == 0:
            return abort(404)
        

        return jsonify({
            'success': True,
            'questions': requested_qustions,
            'totalQuestions': len(questions_list),
            'categories': categories_dict,
            'currentCategory': None
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({'success': True})
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appearpunduits at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(
                question=new_question, 
                answer=new_answer, 
                category=new_category, 
                difficulty=new_difficulty)
            question.insert()
            return jsonify({'success': True})
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.json.get("searchTerm")
        if search_term is None:
            return abort(422)
        results = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        results_paginated = paginated_questions(request, results)
        result_category = [question['category'] for question in results_paginated]
        current_category = result_category[0] if len(result_category) > 0 else None

        return jsonify({
            'success': True,
            'questions': results_paginated,
            'totalQuestions': len(results),
            'currentCategory': current_category
            })



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter(Category.id==category_id).one_or_none()

        if category:
            try:
                cate_questions = Question.query.filter(Question.id==category_id).all()
                cate_questions_list = [question.format() for question in cate_questions]

                return jsonify({
                    'success': True,
                    'questions': cate_questions_list,
                    'totalQuestions': len(cate_questions_list),
                    'currentCategory': category.type
                })
            except:
                abort(422)
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()
        previous_question = body.get('previous_questions')
        category_value = body.get('quiz_category')
        category = Category.query.filter(func.lower(Category.type) == category_value.lower()).one_or_none()
        questions = Question.query.filter(~Question.id.in_(previous_question)).all()
        try: 
            ready_questions = [question for question in questions if question.category == category.id ]
            random_choice = random.choice(ready_questions)
            randomized_question = random_choice.format()

            return jsonify({
                'success': True,
                'question': randomized_question
            })
        except:
            abort(400)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success':False,
            'error': 400,
            'message': 'bad request'
        }), 400        
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error': 404,
            'message':'resource not found',
        }), 404
    
    @app.errorhandler(405)
    def unallowed_method(error):
        return jsonify({
            'success':False,
            'error': 405,
            'message':'method not allowed',
        }), 405
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success':False,
            'error': 422,
            'message':'unprocessable',
        }), 422

    return app

