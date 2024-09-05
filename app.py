#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Define Resource Classes
class HeroResource(Resource):
    def get(self, id=None):
        if id:
            hero = Hero.query.get(id)
            if hero is None:
                abort(404, description="Hero not found")
            return jsonify(hero.to_dict())
        else:
            heroes = Hero.query.all()
            return jsonify([hero.to_dict() for hero in heroes])

class PowerResource(Resource):
    def get(self, id=None):
        if id:
            power = Power.query.get(id)
            if power is None:
                abort(404, description="Power not found")
            return jsonify(power.to_dict())
        else:
            powers = Power.query.all()
            return jsonify([power.to_dict() for power in powers])

    def patch(self, id):
        power = Power.query.get(id)
        if power is None:
            abort(404, description="Power not found")
        
        data = request.get_json()
        description = data.get('description')

        if description:
            if len(description) < 20:
                abort(400, description="Description must be at least 20 characters long.")
            power.description = description
            db.session.commit()
            return jsonify(power.to_dict())
        else:
            abort(400, description="Description field is required.")

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')
        strength = data.get('strength')

        if not all([hero_id, power_id, strength]):
            abort(400, description="Missing required fields")

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if not hero or not power:
            abort(404, description="Hero or Power not found")

        if strength not in ['Strong', 'Weak', 'Average']:
            abort(400, description="Invalid strength value")

        try:
            hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
            db.session.add(hero_power)
            db.session.commit()
            return jsonify(hero_power.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            abort(500, description=f"Server error: {str(e)}")

# Add Resource Routes
api.add_resource(HeroResource, '/heroes', '/heroes/<int:id>')
api.add_resource(PowerResource, '/powers', '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

# Default Route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': str(error)}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': str(error)}), 500

# Run the application
if __name__ == '__main__':
    app.run(port=5555, debug=True)
