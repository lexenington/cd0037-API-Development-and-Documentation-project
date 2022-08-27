import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "victory", 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.  # noqa E501
    """
    # Test pagination and the '/questions' endpoint
    def test_get_paginated_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['questions'], True)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=3000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test GET on '/categories'
    def test_get_questions(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'], True)

    # Test DELETE question
    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    # Test POST new question
    def test_create_new_question(self):
        valid_new_question = {"question": "Who invented the telephone", "answer": "Alexander Graham", "category": "4", "difficulty": 4}  # noqa E501
        res = self.client().post("/questions", json=valid_new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_if_question_creation_fails(self):
        invalid_new_question = {"question": "", "answer": "", "category": '', 'difficulty': 4}  # noqa E501
        res = self.client().post("/questions", json=invalid_new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    # Test POST on question search
    def test_get_question_search_with_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "find"})  # noqa E501
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(len(data['questions']), 1)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'kenya'})  # noqa E501
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(len(data['questions']), 0)

    # Test GET question based on categories on the '/categories/<id>/endpoint'
    def test_get_questions_valid_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['currentCategory'])

    def test_get_questions_invalid_category(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test POST quizzes on the '/quizzes' endpoint
    def test_post_quizzes_success(self):
        quiz_json = {
            'previous_questions': [],
            'quiz_category': 'History'
        }
        res = self.client().post('/quizzes', json=quiz_json)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_questions_invalid_category(self):
        quiz_json_invalid = {
            'previous_questions': [],
            'quiz_category': 'Soccer'
        }
        res = self.client().post('/quizzes', json=quiz_json_invalid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
