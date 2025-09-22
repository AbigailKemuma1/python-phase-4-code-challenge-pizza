import pytest
from faker import Faker
from server.models import Restaurant, Pizza, RestaurantPizza, db
from server.app import create_app

# ---------------------------
# Fixtures
# ---------------------------

@pytest.fixture(scope="module")
def app():
    """Create a Flask app for testing with in-memory SQLite DB."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app  # provide the app to tests
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()

@pytest.fixture
def faker():
    return Faker()

# ---------------------------
# Tests
# ---------------------------

def test_restaurants(client, faker):
    """GET /restaurants"""
    restaurant1 = Restaurant(name=faker.name(), address=faker.address())
    restaurant2 = Restaurant(name=faker.name(), address=faker.address())
    db.session.add_all([restaurant1, restaurant2])
    db.session.commit()

    response = client.get('/restaurants')
    assert response.status_code == 200
    data = response.get_json()
    assert [r['id'] for r in data] == [restaurant1.id, restaurant2.id]
    assert all('restaurant_pizzas' not in r for r in data)

def test_restaurant_by_id(client, faker):
    """GET /restaurants/<id>"""
    restaurant = Restaurant(name=faker.name(), address=faker.address())
    db.session.add(restaurant)
    db.session.commit()

    response = client.get(f'/restaurants/{restaurant.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == restaurant.id
    assert data['name'] == restaurant.name
    assert 'restaurant_pizzas' in data

def test_restaurant_404(client):
    """GET non-existent restaurant returns 404"""
    response = client.get('/restaurants/0')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_delete_restaurant(client, faker):
    """DELETE /restaurants/<id>"""
    restaurant = Restaurant(name=faker.name(), address=faker.address())
    db.session.add(restaurant)
    db.session.commit()

    response = client.delete(f'/restaurants/{restaurant.id}')
    assert response.status_code == 204

    # Verify deletion
    assert Restaurant.query.filter_by(id=restaurant.id).one_or_none() is None

def test_delete_404(client):
    """DELETE non-existent restaurant returns 404"""
    response = client.delete('/restaurants/0')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Restaurant not found"

def test_pizzas(client, faker):
    """GET /pizzas"""
    pizza1 = Pizza(name=faker.name(), ingredients=faker.sentence())
    pizza2 = Pizza(name=faker.name(), ingredients=faker.sentence())
    db.session.add_all([pizza1, pizza2])
    db.session.commit()

    response = client.get('/pizzas')
    assert response.status_code == 200
    data = response.get_json()
    assert [p['id'] for p in data] == [pizza1.id, pizza2.id]
    assert all('restaurant_pizzas' not in p for p in data)

def test_create_restaurant_pizza(client, faker):
    """POST /restaurant_pizzas"""
    pizza = Pizza(name=faker.name(), ingredients=faker.sentence())
    restaurant = Restaurant(name=faker.name(), address=faker.address())
    db.session.add_all([pizza, restaurant])
    db.session.commit()

    response = client.post(
        '/restaurant_pizzas',
        json={
            "price": 10,
            "pizza_id": pizza.id,
            "restaurant_id": restaurant.id
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['price'] == 10
    assert data['pizza_id'] == pizza.id
    assert data['restaurant_id'] == restaurant.id
    assert 'id' in data
    assert 'pizza' in data
    assert 'restaurant' in data

def test_create_restaurant_pizza_validation_error(client, faker):
    """POST /restaurant_pizzas with invalid price returns 400"""
    pizza = Pizza(name=faker.name(), ingredients=faker.sentence())
    restaurant = Restaurant(name=faker.name(), address=faker.address())
    db.session.add_all([pizza, restaurant])
    db.session.commit()

    for invalid_price in [0, 31]:
        response = client.post(
            '/restaurant_pizzas',
            json={
                "price": invalid_price,
                "pizza_id": pizza.id,
                "restaurant_id": restaurant.id
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['errors'] == ["validation errors"]
