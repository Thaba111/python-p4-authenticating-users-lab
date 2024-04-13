#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
import json
from models import User

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        if user:
            # Set user_id in session to authenticate the user
            session['user_id'] = user.id
            return jsonify({'id': user.id, 'username': user.username}), 200
        else:
            return jsonify({'message': 'Invalid username'}), 401
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    
class Logout(Resource):
    def delete(self):
        # Remove user_id from session to log out the user
        session.pop('user_id', None)
        return '', 204

@app.route('/check_session', methods=['GET'])
def check_session():
    try:
        user_id = session.get('user_id')
        if user_id:
            # Query the database for the user using user_id from session
            user = User.query.get(user_id)
            if user:
                return jsonify({'id': user.id, 'username': user.username}), 200
        return jsonify({}), 401
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

#api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
#api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
