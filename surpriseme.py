#!/usr/bin/python

from flask import Flask, jsonify, abort, request, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/surprisemedb'
app.config['SECRET_KEY'] = 'surpriseme'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

import database_models

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = database_models.Users.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = database_models.Users.query.filter_by(user_id=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/surpriseme/v1/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')}) 


@app.route('/surpriseme/v1/adduser', methods=['POST'])
def adduser():
    if not request.json or not 'user_id' in request.json or\
       not 'user_name' in request.json or not 'password' in request.json:
        abort(400)

    user = database_models.Users.query.filter_by(user_id=request.json['user_id']).first()
    if user is not None:
        # existing user
        abort(400)

    content = request.json
    print(content)
    newuser = database_models.Users(content['user_id'], content['user_name'], content.get('email', ''), content.get('phone', ''))
    newuser.hash_password(content['password'])

    db.session.add(newuser)
    db.session.commit()
    u = database_models.Users.query.filter_by(user_id=content['user_id']).first()
    return jsonify({'success' : u.id}), 201


if __name__ == '__main__':
    app.run()
