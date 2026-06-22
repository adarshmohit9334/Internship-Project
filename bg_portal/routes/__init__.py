from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.request_routes import request_bp
from routes.report_routes import report_bp
from routes.approval_routes import approval_bp
from routes.admin_routes import admin_bp
from routes.settings_routes import settings_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)
