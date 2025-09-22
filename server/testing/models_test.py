import pytest
from server.app import create_app
from server.models import db, Restaurant, Pizza, RestaurantPizza
from faker import Faker

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # in-memory DB for tests

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def faker():
    return Faker()

class TestRestaurantPizza:
    """Tests for RestaurantPizza model validations"""

    def test_price_between_1_and_30(self, app, faker):
        pizza = Pizza(name=faker.name(), ingredients="Dough, Sauce, Cheese")
        restaurant = Restaurant(name=faker.name(), address='Main St')
        db.session.add_all([pizza, restaurant])
        db.session.commit()

        rp1 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=1)
        rp2 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=30)
        db.session.add_all([rp1, rp2])
        db.session.commit()

        # Check DB
        assert RestaurantPizza.query.count() == 2

    def test_price_too_low(self, app, faker):
        pizza = Pizza(name=faker.name(), ingredients="Dough, Sauce, Cheese")
        restaurant = Restaurant(name=faker.name(), address='Main St')
        db.session.add_all([pizza, restaurant])
        db.session.commit()

        import pytest
        with pytest.raises(ValueError):
            rp = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=0)
            db.session.add(rp)
            db.session.commit()

    def test_price_too_high(self, app, faker):
        pizza = Pizza(name=faker.name(), ingredients="Dough, Sauce, Cheese")
        restaurant = Restaurant(name=faker.name(), address='Main St')
        db.session.add_all([pizza, restaurant])
        db.session.commit()

        import pytest
        with pytest.raises(ValueError):
            rp = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=31)
            db.session.add(rp)
            db.session.commit()
