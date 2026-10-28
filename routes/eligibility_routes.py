"""Eligibility Explorer routes."""
from flask import Blueprint, render_template, request
from db import execute_query
from services.eligibility_service import get_eligible_students_for_job

eligibility_bp = Blueprint('eligibility', __name__)


@eligibility_bp.route('/')
def explorer():
    jobs = execute_query("""
        SELECT jp.job_id, jp.job_title, c.company_name, jp.status,
               jp.application_deadline, jp.min_cgpa, jp.max_backlogs, jp.eligible_grad_year
        FROM job_postings jp
        INNER JOIN companies c ON c.company_id=jp.company_id
        ORDER BY jp.status, jp.job_title""")

    selected_job_id = request.args.get('job_id', type=int)
    show_ineligible = request.args.get('show_ineligible', '0') == '1'
    search = request.args.get('search', '').strip()

    eligible, ineligible, job = [], [], None
    if selected_job_id:
        result = get_eligible_students_for_job(selected_job_id)
        if result and len(result) == 3:
            eligible, ineligible, job = result
        if search:
            sl = search.lower()
            eligible = [s for s in eligible if sl in s['full_name'].lower() or sl in s['enrollment_no'].lower()]
            ineligible = [s for s in ineligible if sl in s['full_name'].lower() or sl in s['enrollment_no'].lower()]

    return render_template('eligibility/explorer.html', jobs=jobs,
                           selected_job_id=selected_job_id, eligible=eligible,
                           ineligible=ineligible, job=job,
                           show_ineligible=show_ineligible, search=search)
