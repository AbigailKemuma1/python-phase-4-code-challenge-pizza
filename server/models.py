# server/models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # relationship to RestaurantPizza
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    def to_dict(self, include=None, exclude=None):
        # include: list of attributes or relationship names to include
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }
        if include and "restaurant_pizzas" in include:
            data["restaurant_pizzas"] = [rp.to_dict(include=["pizza"]) for rp in self.restaurant_pizzas]
        if exclude:
            for key in exclude:
                data.pop(key, None)
        return data


class Pizza(db.Model):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    def to_dict(self, include=None, exclude=None):
        data = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }
        if include and "restaurant_pizzas" in include:
            data["restaurant_pizzas"] = [rp.to_dict(include=["restaurant"]) for rp in self.restaurant_pizzas]
        if exclude:
            for key in exclude:
                data.pop(key, None)
        return data


class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")

    @validates('price')
    def validate_price(self, key, price):
        if price is None:
            raise ValueError("price must be present")
        if not isinstance(price, int):
            # often requests come as JSON numbers -> Python int, but be safe:
            try:
                price = int(price)
            except Exception:
                raise ValueError("price must be an integer")
        if price < 1 or price > 30:
            raise ValueError("price must be between 1 and 30")
        return price

    def to_dict(self, include=None, exclude=None):
        data = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }
        if include:
            if "pizza" in include:
                data["pizza"] = self.pizza.to_dict()
            if "restaurant" in include:
                data["restaurant"] = self.restaurant.to_dict()
        if exclude:
            for key in exclude:
                data.pop(key, None)
        return data
