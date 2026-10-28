"""Dashboard routes - main dashboard with live statistics."""
from flask import Blueprint, render_template
from services.dashboard_service import (
    get_dashboard_stats, get_application_status_chart,
    get_department_placement_chart, get_recent_applications,
    get_upcoming_interviews
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    stats = get_dashboard_stats()
    app_status_chart = get_application_status_chart()
    dept_chart = get_department_placement_chart()
    recent_apps = get_recent_applications()
    upcoming = get_upcoming_interviews()
    return render_template('dashboard/index.html',
                           stats=stats,
                           app_status_chart=app_status_chart,
                           dept_chart=dept_chart,
                           recent_apps=recent_apps,
                           upcoming_interviews=upcoming)
