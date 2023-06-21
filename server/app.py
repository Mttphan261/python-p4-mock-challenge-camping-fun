#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app)

db.init_app(app)

@app.route('/')
def home():
    return 'This is the home page!'

class Campers(Resource):
    def get(self):
        campers = [c.to_dict(only=('id', 'name', 'age')) for c in Camper.query.all()]
        return campers, 200
    
    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data.get('name'),
                age = data.get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(only=('id', 'age', 'name')), 201
        except:
            return {'error': ['validation errors']}, 400
    
api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        try:
            camper = Camper.query.filter_by(id=id).first()
            return camper.to_dict(), 200
        except:
            return {'error': 'Camper not found.'}, 404
    
    def patch(self, id):
        data = request.get_json()
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            try:
                for attr in data:
                    setattr(camper, attr, data.get(attr))
                db.session.add(camper)
                db.session.commit()
                return camper.to_dict(only=('id', 'name', 'age')), 200
            except:
                return {'errors': ['validation errors']}, 422
        else:
            return {'error': 'Camper not found.'}, 404
        
api.add_resource(CamperByID, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = [a.to_dict(only=("id", "name", "difficulty")) for a in Activity.query.all()]
        return activities, 200

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def delete(self, id):
        try:
            activity = Activity.query.filter_by(id=id).first()
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        except:
            return {'error': 'Activity not found'}, 404
        
api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id = data.get('camper_id'),
                activity_id = data.get('activity_id'),
                time = data.get('time')
            )
            db.session.add(new_signup)
            db.session.commit()
            return new_signup.to_dict(), 201
        except:
            return {'error': ['validation errors']}, 400

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
