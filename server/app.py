# server/app.py
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from server.models import db, Restaurant, Pizza, RestaurantPizza

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    # -----------------------
    # Routes
    # -----------------------

    @app.route('/')
    def index():
        return jsonify({"message": "Flask app is working!"})

    # GET all restaurants
    @app.route('/restaurants', methods=['GET'])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([{
            "id": r.id,
            "name": r.name,
            "address": r.address
        } for r in restaurants])

    # GET restaurant by ID
    @app.route('/restaurants/<int:id>', methods=['GET'])
    def get_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return jsonify({"error": "Restaurant not found"}), 404
        return jsonify({
            "id": r.id,
            "name": r.name,
            "address": r.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza": {"id": rp.pizza.id, "name": rp.pizza.name}
                }
                for rp in r.restaurant_pizzas
            ]
        })

    # DELETE restaurant by ID
    @app.route('/restaurants/<int:id>', methods=['DELETE'])
    def delete_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(r)
        db.session.commit()
        return '', 204

    # GET all pizzas
    @app.route('/pizzas', methods=['GET'])
    def get_pizzas():
        pizzas = Pizza.query.all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "ingredients": p.ingredients
        } for p in pizzas])

    # POST create RestaurantPizza
    @app.route('/restaurant_pizzas', methods=['POST'])
    def create_restaurant_pizza():
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        # Validation
        if price is None or pizza_id is None or restaurant_id is None:
            return jsonify({"errors": ["validation errors"]}), 400
        if not (1 <= price <= 30):
            return jsonify({"errors": ["validation errors"]}), 400

        rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(rp)
        db.session.commit()

        return jsonify({
            "id": rp.id,
            "price": rp.price,
            "pizza_id": rp.pizza_id,
            "restaurant_id": rp.restaurant_id,
            "pizza": {"id": rp.pizza.id, "name": rp.pizza.name},
            "restaurant": {"id": rp.restaurant.id, "name": rp.restaurant.name}
        }), 201

    return app


# Allow running directly
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
