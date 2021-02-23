from flask import Flask
from synonym.client import Synonyms
from synonym.apps.project import create_project_app
from synonym.apps.category import create_category_app
from synonym.apps.origin import create_origin_app
from synonym.apps.synonym import create_synonym_app
from synonym.apps import crate_user_app

app = Flask(__name__)
bp = create_project_app()
ca_bp = create_category_app()
or_bp = create_origin_app()
sy_bp = create_synonym_app()
app = crate_user_app(app)
app.register_blueprint(bp)
app.register_blueprint(ca_bp)
app.register_blueprint(or_bp)
app.register_blueprint(sy_bp)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050)