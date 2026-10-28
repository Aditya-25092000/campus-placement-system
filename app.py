"""Campus Placement & Eligibility Management System - Main Application."""
from flask import Flask, redirect, url_for, session, flash
from config import Config
from services.auth_service import seed_admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.student_routes import student_bp
    from routes.company_routes import company_bp
    from routes.job_routes import job_bp
    from routes.application_routes import application_bp
    from routes.interview_routes import interview_bp
    from routes.offer_routes import offer_bp
    from routes.eligibility_routes import eligibility_bp
    from routes.report_routes import report_bp
    from routes.showcase_routes import showcase_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(company_bp, url_prefix='/companies')
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(application_bp, url_prefix='/applications')
    app.register_blueprint(interview_bp, url_prefix='/interviews')
    app.register_blueprint(offer_bp, url_prefix='/offers')
    app.register_blueprint(eligibility_bp, url_prefix='/eligibility')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(showcase_bp, url_prefix='/showcase')

    @app.before_request
    def require_login():
        """Protect all routes except login and static files."""
        from flask import request
        allowed = ['auth.login', 'static']
        if request.endpoint and not any(request.endpoint.startswith(a) for a in allowed):
            if 'admin_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_globals():
        return {
            'current_user': session.get('admin_name', ''),
            'app_name': 'Campus Placement System'
        }

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    # Seed admin user
    with app.app_context():
        try:
            seed_admin()
        except Exception as e:
            print(f"Warning: Could not seed admin user: {e}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
