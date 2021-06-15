import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import NotFound, Unauthorized

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_short_drinks(payload):
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    if len(drinks) == 0:
        raise NotFound()
    else:
        response = {
            'success': True,
            'status_code': 200,
            'drinks': drinks
        }
        return jsonify(response)



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_long_drinks(payload):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    if len(drinks) == 0:
        raise NotFound()
    else:
        response = {
            'success': True,
            'status_code': 200,
            'drinks': drinks
            }
        return jsonify(response)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        body = request.get_json()
        drink = Drink()
        drink.title = body["title"]
        drink.recipe = json.dumps(body["recipe"])
        drink.insert()
        response = {
            'success': True,
            'status_code': 200,
            'drinks': drink.long()
        }
        return jsonify(response)
    except Exception:
        raise Unauthorized()


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    try:
        if id is None:
            raise NotFound()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if 'title' in body:
            drink.title = body["title"]
        if 'recipe' in body:
            drink.recipe = body["recipe"]        
        drink.update()
        patch_drink = Drink.query.filter(Drink.id == id).one_or_none()
        response = {
            'success': True,
            'status_code': 200,
            'drinks': patch_drink.long(),
        }
        return jsonify(response)
    except Exception:
        raise Unauthorized()


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    try:
        if id is None:
            raise NotFound()
        else:
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if drink is None:
                raise NotFound()
            else:
                drink.delete()
                response = {
                        'success': True,
                        'status_code': 200,
                        'delete': id
                }
                return jsonify(response)
    except Exception:
        raise Unauthorized()

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
        }), 404

@app.errorhandler(401)
def Unauthorized_client(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized client status"
        }), 401