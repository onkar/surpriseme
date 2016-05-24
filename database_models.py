from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from surpriseme import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


Veg = 1
NonVeg = 2
Chickenterian = 3
Eggiterian = 4

Mild = 1
Medium = 2
Hot = 3
XHot = 4

Appetizer = 1
Entre = 2
Dessert = 3
Soup = 4
HotDrink = 5
ColdDrink = 6

Sweet = 1
Sour = 2
Bitter = 3
Bland = 4
Neutral = 5
Spicy = 6

Heavy = 1
Light = 2
Neutral = 3


# This table will hold data for user
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    user_id = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    phone = db.Column(db.String(11))
    address = db.Column(db.String(100))
    zipcode = db.Column(db.Integer)
    is_veg = db.Column(db.Integer)
    spice_level = db.Column(db.Integer)
    dob = db.Column(db.DateTime)

    def __init__(self, user_id, name, email=None, phone=None, address=None, dob=None, is_veg=Veg,
                 spice_level=Mild):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.dob = dob
        self.is_veg = is_veg
        self.spice_level = spice_level

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 60000):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'user_id': self.user_id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = Users.query.filter_by(user_id=data['user_id']).first()
        return user


#class DishRestaurant(db.Model):
#    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurant.id'), primary_key=True)
#    dish_id = db.Column(db.Integer, db.ForeignKey('Dish.id'), primary_key=True)
#    serves = db.Column(db.Integer) # serves how many people in a single serving
#    rating = db.Column(db.Integer) # dish rating in that particular restaurant
#    price = db.Column(db.Float)
    
    
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    address = db.Column(db.String(100))
    zipcode = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    rating = db.Column(db.Integer)
    price = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    close_time = db.Column(db.DateTime)
#    dishes = db.relationship('Dish', secondary='DishRestaurant', lazy='dynamic')
 
    def __init__(self, name, address, zipcode, latitude, longitude, rating, price,
                 start_time, close_time):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.latitude = latitude
        self.longitude = longitude
        self.rating = rating
        self.price = price
        self.start_time = start_time
        self.close_time = close_time 
#        self.dishes = []


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    food_type = db.Column(db.Integer)
    cuisine = db.Column(db.String(20))
    exotic_level = db.Column(db.Integer)
    standalone_dish = db.Column(db.Boolean)
    dish_type = db.Column(db.Integer)
    taste = db.Column(db.Integer)
    food_feel = db.Column(db.Integer)
 
    def __init__(self, name, food_type, cuisine, exotic_level, standalone_dish,
             dish_type=Entre, taste=Neutral, food_feel=Neutral):
        self.name = name
        self.food_type = food_type
        self.cuisine = cuisine
        self.exotic_level = exotic_level
        self.standalone_dish = standalone_dish
        self.dish_type = dish_type
        self.taste = taste
        self.food_feel = food_feel


class UserRestaurantExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    rating = db.Column(db.Integer)

    def __init__(self, user_id, restaurant_id, rating=0):
        user_id = user_id
        restaurant_id = restaurant_id
        rating = 0


class UserDishExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'))
    rating = db.Column(db.Integer)

    def __init__(self, user_id, dish_id, rating=0):
        user_id = user_id
        dish_id = dish_id
        rating = 0



class Surprise(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), primary_key=True)
    user_experience_factor = db.Column(db.Integer)
 
    def __init__(self, user_experience_factor):
        self.user_experience_factor = user_experience_factor


class UserOrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
    date_of_order = db.Column(db.DateTime)
    dish_id = db.Column(db.Integer)

    def __init__(self, user_id, restaurant_id, dish_id):
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.dish_id = dish_id
        self.date_of_order = datetime.now()


class UserRestaurantVisitCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    num_visits = db.Column(db.Integer)

    def __init__(self, user_id, restaurant_id):
        user_id = user_id
        restaurant_id = restaurant_id
        num_visits = 1


class SurpriseMeUser:
    def __init__(self, user):
        surpriseMeUser = user    

    def getUserRestaurantExperience(self, restaurant_name):
        res = Restaurant.query.filter_by(name=restaurant_name).first()
        if res is not None:
            userExp = UserRestaurantExperience.query.filter_by(restaurant_id = res.id, user_id = surpriseMeUser.id).first()
            if userExp is not None:
                return userExp.rating
        return 0

    def setUserRestaurantExperience(self, restaurant_name, rating):
        res = Restaurant.query.filter_by(name=restaurant_name).first()
        if res is not None:
            userExp = UserRestaurantExperience.query.filter_by(restaurant_id = res.id, user_id = surpriseMeUser.id).first()
            if userExp is not None:
                userExp.rating = rating
            else:
                userExp = UserRestaurantExperience(surpriseMeUser.id, res.id, rating)
            db.session.commit()

    def getUserDishExperience(self, dish_name):
        res = Dish.query.filter_by(name=dish_name).first()
        if res is not None:
            userExp = UserDishExperience.query.filter_by(dish_id = res.id, user_id = surpriseMeUser.id).first()
            if userExp is not None:
                return userExp.rating
        return 0

    def setUserDishExperience(self, dish_name, rating):
        res = Dish.query.filter_by(name=dish_name).first()
        if res is not None:
            userExp = UserDishExperience.query.filter_by(dish_id = res.id, user_id = surpriseMeUser.id).first()
            if userExp is not None:
                userExp.rating = rating
            else:
                userExp = UserDishExperience(surpriseMeUser.id, res.id, rating)
            db.session.commit()


    def getNumTimesUsedRestaurant(self, restaurant_name):
        res = Restaurant.query.filter_by(name=restaurant_name).first()
        if res is not None:
            numVisited = UserRestaurantVisitCount.query.filter_by(restaurant_id = res.id, user_id = surpriseMeUser.id).first()
            if numVisited is not None:
                return numVisited.num_visits
        return 0

    def incNumTimesUsedRestaurant(self, restaurant_name):
        res = Restaurant.query.filter_by(name=restaurant_name).first()
        if res is not None:
            numVisited = UserRestaurantVisitCount.query.filter_by(restaurant_id = res.id, user_id = surpriseMeUser.id).first()
            if numVisited is not None:
                ++numVisited.num_visits
            else:
                uvCount = UserRestaurantVisitCount(surpriseMeUser.id, res.id)
            db.session.commit()
 
    def getNumTimesServedDish(self, dish_name):
        pass


#def getDishProperties(dish_name):

#def getGlobalDishExperience(dish_name):

#def getGlobalRestaurantExperience(restaurant_name):
