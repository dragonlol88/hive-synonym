import os
import typing
import uuid
import datetime

from flask import Blueprint, request, jsonify, send_file

from synonym.parse import FileParser, Sinker, Exporter
from synonym.response import OriginResponse, SynonymFileOutput

from . import db_client


def create_origin_app():
    origin_bp = Blueprint('origin_app', __name__)

    @origin_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins', methods=['POST'])
    def create_origin(pjt_id, category_id):

        params = request.get_json()
        synm_keywords = params.pop("synm_keywords", None)
        assert synm_keywords

        request_params = {
            'pjt_id': pjt_id,
            'category_id': category_id,
            'synm_keyword': synm_keywords,
            'fields': ['pjt_id', 'category_id', 'origin_keyword', 'synonym'],
            'response_model': OriginResponse
        }
        request_params.update(params)

        r = db_client.origin('insert', **request_params)

        return jsonify(r)


    @origin_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/bulk', methods=['POST'])
    def create_origin_bulk(pjt_id, category_id):

        synonym_file = request.files.get('synonym_file', '')
        job_id = uuid.uuid4()
        new_filename = "{}.xlsx".format(job_id)
        path = os.path.join('./', new_filename)
        synonym_file.save(path)
        fp = FileParser(path, Sinker, output_model=SynonymFileOutput)
        request_params = {
            'pjt_id': pjt_id,
            'category_id': category_id,
            'bulk': fp.process(),
            'fields': ['pjt_id', 'category_id', 'origin_keyword', 'synonym'],
            'response_model': typing.List[OriginResponse]
        }
        r = db_client.origin('bulk_insert', **request_params)
        fp.remove()
        return r

    @origin_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/downloads', methods=['GET'])
    def export_file(pjt_id, category_id):
        category_name = request.args.get('category_name', None)
        file_name = "{}-synonyms-{}.xlsx".format(category_name, datetime.datetime.now().strftime('%Y%m%d%H%M'))
        path = os.path.join('./', file_name)

        where = []
        on_off = {}
        where.append(('pjt_id', 'on_off'))
        where.append(('category_id', 'on_off'))
        on_off['pjt_id'] = True
        on_off['category_id'] = True

        request_params = {
            'category_id': category_id,
            'pjt_id': pjt_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[OriginResponse]
        }
        response = db_client.origin('find', **request_params)
        fp = FileParser(path, Exporter, response['data'])
        fp.process()
        resp = send_file(path,
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         attachment_filename=file_name)
        fp.remove()
        return resp


    @origin_bp.route('/api/origins', methods=['GET'])
    def get_origin():
        origin_keyword = request.args.get('q', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 0))

        where = []
        on_off = {}
        if origin_keyword:
            where.append(('origin_keyword', 'like'))

        request_params = {
            'origin_keyword': origin_keyword,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[OriginResponse]
        }
        response = db_client.origin('find', **request_params)

        return jsonify(response)

    @origin_bp.route('/api/pjt/<int:pjt_id>/origins', methods=['GET'])
    def get_origin_per_project(pjt_id):

        origin_keyword = request.args.get('q', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 0))

        where = []
        on_off = {}

        where.append(('pjt_id', 'on_off'))
        on_off['pjt_id'] = True
        if origin_keyword:
            where.append(('origin_keyword', 'like'))

        request_params = {
            'pjt_id': pjt_id,
            'origin_keyword': origin_keyword,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[OriginResponse]
        }
        response = db_client.origin('find', **request_params)


        return jsonify(response)


    @origin_bp.route('/api/pjt/<int:pjt_id>/categories/<int:category_id>/origins', methods=['GET'])
    def get_origin_per_category(pjt_id, category_id):
        origin_keyword = request.args.get('q', None)
        page = int(request.args.get('page', 0))
        size = int(request.args.get('size', 0))

        where = []
        on_off = {}

        where.append(('pjt_id', 'on_off'))
        where.append(('category_id', 'on_off'))
        on_off['pjt_id'] = True
        on_off['category_id'] = True

        if origin_keyword:
            where.append(('origin_keyword', 'like'))

        request_params = {
            'category_id': category_id,
            'pjt_id': pjt_id,
            'origin_keyword': origin_keyword,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[OriginResponse]
        }
        response = db_client.origin('find', **request_params)

        return jsonify(response)


    @origin_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/<int:origin_id>', methods=['PUT'])
    def update_origin(pjt_id, category_id, origin_id):
        where = []
        on_off = {}
        fields = []
        params = request.get_json()

        assert params['origin_keyword']

        where.append(('id', 'on_off'))
        on_off['id'] = True
        fields.append('origin_keyword')

        request_params = {
            'id': origin_id,
            'where': where,
            'on_off': on_off,
            'fields': fields,
            'response_model': typing.List[OriginResponse]
        }
        request_params.update(params)
        r = db_client.origin('update', **request_params)
        return jsonify(r)


    @origin_bp.route('/api/pjts/<int:pjt_id>/categories/<int:category_id>/origins/<int:origin_id>', methods=['DELETE'])
    def delete_origin(pjt_id, category_id, origin_id):
        where = []
        on_off = {}
        fields = []

        where.append(('id', 'on_off'))
        on_off['id'] = True

        request_params = {
            'id': origin_id,
            'where': where,
            'on_off': on_off,
            'response_model': typing.List[OriginResponse]
        }
        r = db_client.origin('delete', **request_params)
        return jsonify(r)

    return origin_bp
