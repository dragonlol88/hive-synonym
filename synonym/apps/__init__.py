from synonym.client import Synonyms
from flask import request, jsonify
from ..response import UserResponse
import typing


def crate_user_app(app):

    @app.route('/api/users', methods=['POST'])
    def create_user():
        params = request.get_json()

        request_params = {
            'fields': ['user_id', 'password'],
            'response_model': UserResponse
        }
        request_params.update(params)

        r = db_client.user('insert', **request_params)

        return jsonify(r)

    @app.route('/api/users', methods=['GET'])
    def get_user():
        user_id = request.args.get('user_id', None)
        where = []
        on_off = {}

        if user_id:
            where.append(('user_id', 'like'))

        request_params = {
            'user_id': user_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[UserResponse]
        }

        r = db_client.user('find', **request_params)

        return jsonify(r)

    return app

syn = Synonyms()
db_client = syn.db
