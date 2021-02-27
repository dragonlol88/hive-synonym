import typing
from . import db_client

from flask import Blueprint, request, jsonify
from synonym.response import CategoryResponse

def create_category_app():
    category_bp = Blueprint('category_app', __name__)

    @category_bp.route('/api/pjts/<int:pjt_id>/categories', methods=['POST'])
    def create_category(pjt_id):

        params = request.get_json()

        request_params = {
            'pjt_id': pjt_id,
            'fields': ['category_name', 'pjt_id'],
            'response_model': CategoryResponse
        }
        request_params.update(params)

        response = db_client.category('insert', **request_params)
        return jsonify(response)

    @category_bp.route('/api/pjts/<int:pjt_id>/categories', methods=['GET'])
    def get_category(pjt_id):

        where = []
        on_off = {}

        category_name = request.args.get('q', None)
        page = int(request.args.get('page', 0)) #int
        size = int(request.args.get('size', 0)) #int

        where.append(('pjt_id', 'on_off'))
        on_off['pjt_id'] = True
        if category_name:
            where.extend(['and', ('category_name', 'like')])
            on_off['category_name'] = True


        request_params = {
            'pjt_id': pjt_id,
            'category_name': category_name,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[CategoryResponse]
        }
        r = db_client.category('find', **request_params)
        return jsonify(r)


    @category_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>', methods=['PUT'])
    def update_category(pjt_id, category_id):
        where = []
        on_off = {}
        fields = []
        params = request.get_json()

        assert params['category_name']

        where.append(('id', 'on_off'))
        on_off['id'] = True
        fields.append('category_name')

        request_params = {
            'id': category_id,
            'where': where,
            'on_off': on_off,
            'fields': fields,
            'response_model': typing.List[CategoryResponse]
        }
        request_params.update(params)
        r = db_client.category('update', **request_params)
        return jsonify(r)

    @category_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>', methods=['DELETE'])
    def delete_category(pjt_id, category_id):
        where = []
        on_off = {}
        fields = []

        where.append(('id', 'on_off'))
        on_off['id'] = True

        request_params = {
            'id': category_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[CategoryResponse]
        }
        r = db_client.category('delete', **request_params)
        return jsonify(r)

    return category_bp
