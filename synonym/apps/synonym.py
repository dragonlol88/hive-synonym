from flask import Blueprint, request, jsonify
import typing
from synonym.response import SynonymResponse
from . import db_client

def create_synonym_app():

    synonym_bp = Blueprint('synonym_app', __name__)
    @synonym_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/<int:origin_id>/synms', methods=['POST'])
    def create_synonym(pjt_id, category_id, origin_id):
        params = request.get_json()

        request_params = {
            'pjt_id': pjt_id,
            'category_id': category_id,
            'origin_id': origin_id,
            'fields': ['pjt_id', 'category_id', 'origin_id', 'synm_keyword'],
            'response_model': SynonymResponse
        }
        request_params.update(params)

        r = db_client.synonym('insert', **request_params)

        return jsonify(r)



    @synonym_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/<int:origin_id>/synms/<int:synm_id>', methods=['DELETE'])
    def delete_synonym(pjt_id, category_id, origin_id, synm_id):
        where = []
        on_off = {}

        where.append(('id', 'on_off'))
        on_off['id'] = True

        request_params = {
            'id': synm_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[SynonymResponse]
        }
        r = db_client.synonym('delete', **request_params)
        return jsonify(r)

    return synonym_bp