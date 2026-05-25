"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
 
app = Flask(__name__)
app.url_map.strict_slashes = False
 
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
 
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
 
@app.route('/')
def sitemap():
    return generate_sitemap(app)
 
@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200
 
@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify({"count": len(people), "results": [p.serialize() for p in people]}), 200
 
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify(person.serialize()), 200
 
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify({"count": len(planets), "results": [p.serialize() for p in planets]}), 200
 
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200
 
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify({"count": len(users), "results": [u.serialize() for u in users]}), 200
 
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = request.args.get("user_id", 1, type=int)
    user = User.query.get_or_404(current_user_id)
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify({"user": user.username, "favorites": [f.serialize() for f in favorites]}), 200
 
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = request.args.get("user_id", 1, type=int)
    Planet.query.get_or_404(planet_id)
    existing = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if existing:
        return jsonify({"msg": "Planet already in favorites"}), 409
    fav = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites", "favorite": fav.serialize()}), 201
 
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = request.args.get("user_id", 1, type=int)
    People.query.get_or_404(people_id)
    existing = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if existing:
        return jsonify({"msg": "Person already in favorites"}), 409
    fav = Favorite(user_id=current_user_id, people_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites", "favorite": fav.serialize()}), 201
 
@app.route('/people', methods=['POST'])
def create_person():
    body = request.get_json()
    if not body or not body.get("name"):
        return jsonify({"msg": "Field 'name' is required"}), 400
    person = People(
        name=body.get("name"),
        height=body.get("height"),
        mass=body.get("mass"),
        hair_color=body.get("hair_color"),
        skin_color=body.get("skin_color"),
        eye_color=body.get("eye_color"),
        birth_year=body.get("birth_year"),
        gender=body.get("gender")
    )
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 201
 
@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = People.query.get_or_404(people_id)
    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400
    person.name = body.get("name", person.name)
    person.height = body.get("height", person.height)
    person.mass = body.get("mass", person.mass)
    person.hair_color = body.get("hair_color", person.hair_color)
    person.skin_color = body.get("skin_color", person.skin_color)
    person.eye_color = body.get("eye_color", person.eye_color)
    person.birth_year = body.get("birth_year", person.birth_year)
    person.gender = body.get("gender", person.gender)
    db.session.commit()
    return jsonify(person.serialize()), 200
 
@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get_or_404(people_id)
    db.session.delete(person)
    db.session.commit()
    return jsonify({"msg": f"Person {people_id} deleted"}), 200
 
@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()
    if not body or not body.get("name"):
        return jsonify({"msg": "Field 'name' is required"}), 400
    planet = Planet(
        name=body.get("name"),
        rotation_period=body.get("rotation_period"),
        orbital_period=body.get("orbital_period"),
        diameter=body.get("diameter"),
        climate=body.get("climate"),
        gravity=body.get("gravity"),
        terrain=body.get("terrain"),
        population=body.get("population")
    )
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201
 
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400
    planet.name = body.get("name", planet.name)
    planet.rotation_period = body.get("rotation_period", planet.rotation_period)
    planet.orbital_period = body.get("orbital_period", planet.orbital_period)
    planet.diameter = body.get("diameter", planet.diameter)
    planet.climate = body.get("climate", planet.climate)
    planet.gravity = body.get("gravity", planet.gravity)
    planet.terrain = body.get("terrain", planet.terrain)
    planet.population = body.get("population", planet.population)
    db.session.commit()
    return jsonify(planet.serialize()), 200
 
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": f"Planet {planet_id} deleted"}), 200
 
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = request.args.get("user_id", 1, type=int)
    fav = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first_or_404()
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": f"Planet {planet_id} removed from favorites"}), 200
 
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = request.args.get("user_id", 1, type=int)
    fav = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first_or_404()
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": f"Person {people_id} removed from favorites"}), 200
 
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)