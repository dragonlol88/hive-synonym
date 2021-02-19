from flask import Blueprint, request, jsonify

def create_synonyms_rest_app(app):
    synonym_api_bp = Blueprint('synonyms_rest_apis', __name__)

    @synonym_api_bp.route('/projects', methods=['POST'])
    def create_project():
        a = request.get_json()


    return synonym_api_bp