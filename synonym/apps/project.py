import typing
from flask import Blueprint, request, jsonify
from . import db_client
from synonym.response import (
     ProjectResponse,
     project_find_pre_process
)

def create_project_app():
    bp = Blueprint('project_app', __name__)

    @bp.route('/api/pjts', methods=['POST'])
    def create_project():
        params = request.get_json()
        user_id = request.headers.get('id')

        user_ids = params.pop('members', None)
        assert user_ids

        user_ids.append(user_id)
        request_params = {
                    'user_id': user_ids,
                    'fields' : ['pjt_name', 'pjt_user'],
                    'response_model': ProjectResponse
        }
        request_params.update(params)
        response = db_client.project('insert', **request_params)
        return jsonify(response)

    @bp.route('/api/pjts', methods=['GET'])
    def get_project():
        ismine = int(request.args.get('ismine', None))
        pjt_name = request.args.get('q', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 0))

        user_id = int(request.headers.get("id", None))

        where = []
        on_off = {}

        if not ismine:
            return get_all_project(pjt_name, page, size)

        where.append(('id', 'on_off'))
        on_off['id'] = True
        request_params = {
                        'id': user_id,
                        'pjt_name': pjt_name,
                        'where': where,
                        'on_off': on_off,
                        'page': page,
                        'size': size,
                        'response_model': typing.List[ProjectResponse],
                        'response_preprocess': project_find_pre_process
                    }
        response = db_client.find_project_per_user('find', **request_params)

        return jsonify(response)


    def get_all_project(pjt_name, page, size):

        where = []
        on_off = {}
        if pjt_name:
            where.append(('pjt_name', 'like'))
            on_off['pjt_name'] = True

        r = db_client.project('find',
                               pjt_name=pjt_name,
                               where=where,
                               on_off=on_off,
                               page=page,
                               size=size,
                               response_model=typing.List[ProjectResponse])
        return jsonify(r)



    @bp.route('/api/pjts/<int:pjt_id>', methods=['PUT'])
    def update_project(pjt_id):
        where = []
        on_off = {}
        fields = []
        params = request.get_json()

        assert params['pjt_name']

        where.append(('id', 'on_off'))
        on_off['id'] = True
        fields = ['pjt_name']

        request_params = {
                     'id': pjt_id,
                     'where': where,
                     'on_off': on_off,
                     'fields': fields,
                     'response_model': typing.List[ProjectResponse]
                }
        request_params.update(params)
        r = db_client.project('update', **request_params)
        return jsonify({'response': r})

    @bp.route('/api/pjts/<int:pjt_id>', methods=['DELETE'])
    def delete_project(pjt_id):
        where = []
        on_off = {}
        fields = []

        where.append(('id', 'on_off'))
        on_off['id'] = True

        request_params = {
            'id': pjt_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[ProjectResponse]
        }
        r = db_client.project('delete', **request_params)
        return jsonify(r)

    return bp