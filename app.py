from flask import Flask, redirect, url_for

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from extensions import init_supabase
    init_supabase(app)

    # Register Blueprints
    from routes.auth_routes import bp as auth_bp
    from routes.dashboard_routes import bp as dashboard_bp
    from routes.request_routes import bp as request_bp
    from routes.report_routes import bp as report_bp
    from routes.approval_routes import bp as approval_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(approval_bp)

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.home'))

    @app.before_request
    def mock_login():
        from flask import session
        session['user_id'] = '00000000-0000-0000-0000-000000000000'
        session['user_name'] = 'Test Admin'
        session['role'] = 'admin'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
