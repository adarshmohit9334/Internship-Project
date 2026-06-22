from flask import Flask
from config import Config
from extensions import init_extensions
from routes import register_blueprints
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.permanent_session_lifetime = timedelta(hours=8)
    init_extensions(app)
    register_blueprints(app)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
