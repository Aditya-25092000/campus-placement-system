"""Application management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
from services.eligibility_service import check_student_eligibility
from config import Config

application_bp = Blueprint('applications', __name__)


@application_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    company_filter = request.args.get('company', '', type=str)
    dept_filter = request.args.get('department', '', type=str)
    per_page = Config.ITEMS_PER_PAGE
    conditions, params = [], []
    if search:
        conditions.append("(s.full_name LIKE %s OR s.enrollment_no LIKE %s OR jp.job_title LIKE %s)")
        params.extend([f'%{search}%'] * 3)
    if status_filter:
        conditions.append("a.status = %s"); params.append(status_filter)
    if company_filter:
        conditions.append("jp.company_id = %s"); params.append(company_filter)
    if dept_filter:
        conditions.append("s.department_id = %s"); params.append(dept_filter)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    total = execute_query(f"""
        SELECT COUNT(*) AS total FROM applications a
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id {where}""",
        tuple(params) if params else None, fetchone=True)['total']
    offset = (page - 1) * per_page
    apps = execute_query(f"""
        SELECT a.*, s.full_name, s.enrollment_no, s.student_id,
               d.dept_name, jp.job_title, jp.job_id, c.company_name
        FROM applications a
        INNER JOIN students s ON s.student_id = a.student_id
        INNER JOIN departments d ON d.department_id = s.department_id
        INNER JOIN job_postings jp ON jp.job_id = a.job_id
        INNER JOIN companies c ON c.company_id = jp.company_id
        {where} ORDER BY a.applied_date DESC LIMIT %s OFFSET %s""",
        tuple(params + [per_page, offset]))
    companies = execute_query("SELECT company_id,company_name FROM companies ORDER BY company_name")
    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    total_pages = (total + per_page - 1) // per_page
    return render_template('applications/index.html', applications=apps,
                           companies=companies, departments=departments,
                           page=page, total_pages=total_pages, total=total,
                           search=search, status_filter=status_filter,
                           company_filter=company_filter, dept_filter=dept_filter)


@application_bp.route('/add', methods=['GET', 'POST'])
def add():
    students = execute_query("""
        SELECT s.student_id, s.enrollment_no, s.full_name, d.dept_name
        FROM students s INNER JOIN departments d ON d.department_id=s.department_id
        ORDER BY s.full_name""")
    jobs = execute_query("""
        SELECT jp.job_id, jp.job_title, c.company_name
        FROM job_postings jp INNER JOIN companies c ON c.company_id=jp.company_id
        WHERE jp.status='Active' AND jp.application_deadline>=CURDATE()
        ORDER BY jp.job_title""")
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        job_id = request.form.get('job_id', type=int)
        if not student_id or not job_id:
            flash('Please select both a student and a job.', 'danger')
            return render_template('applications/form.html', students=students, jobs=jobs,
                                   application=request.form, is_edit=False)
        elig = check_student_eligibility(student_id, job_id)
        if not elig['eligible']:
            flash(f"Student not eligible: {'; '.join(elig['reasons'])}", 'danger')
            return render_template('applications/form.html', students=students, jobs=jobs,
                                   application=request.form, is_edit=False)
        try:
            aid, _ = execute_update(
                "INSERT INTO applications (student_id, job_id, status) VALUES (%s,%s,'Applied')",
                (student_id, job_id))
            flash('Application submitted!', 'success')
            return redirect(url_for('applications.view', application_id=aid))
        except Exception as e:
            msg = str(e)
            if 'Duplicate' in msg or '45000' in msg:
                flash('This student already applied for this job.', 'danger')
            elif 'not currently active' in msg.lower():
                flash('This job is not active.', 'danger')
            elif 'deadline' in msg.lower():
                flash('Application deadline has passed.', 'danger')
            else:
                flash(f'Error: {msg}', 'danger')
    return render_template('applications/form.html', students=students, jobs=jobs,
                           application={}, is_edit=False)


@application_bp.route('/<int:application_id>')
def view(application_id):
    app = execute_query("""
        SELECT a.*, s.full_name, s.enrollment_no, s.student_id, s.cgpa,
               d.dept_name, jp.job_title, jp.job_id, jp.job_type,
               c.company_name, c.company_id
        FROM applications a
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN departments d ON d.department_id=s.department_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id
        INNER JOIN companies c ON c.company_id=jp.company_id
        WHERE a.application_id=%s""", (application_id,), fetchone=True)
    if not app:
        flash('Application not found.', 'warning')
        return redirect(url_for('applications.index'))
    interviews = execute_query(
        "SELECT * FROM interview_rounds WHERE application_id=%s ORDER BY scheduled_date",
        (application_id,))
    offer = execute_query("SELECT * FROM offers WHERE application_id=%s",
                          (application_id,), fetchone=True)
    return render_template('applications/view.html', application=app,
                           interviews=interviews, offer=offer)


@application_bp.route('/<int:application_id>/update-status', methods=['POST'])
def update_status(application_id):
    new_status = request.form.get('status', '').strip()
    valid = ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected', 'Withdrawn']
    if new_status not in valid:
        flash('Invalid status.', 'danger')
        return redirect(url_for('applications.view', application_id=application_id))
    try:
        execute_update("UPDATE applications SET status=%s WHERE application_id=%s",
                       (new_status, application_id))
        flash(f'Status updated to {new_status}.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('applications.view', application_id=application_id))


@application_bp.route('/<int:application_id>/delete', methods=['POST'])
def delete(application_id):
    try:
        execute_update("DELETE FROM applications WHERE application_id=%s", (application_id,))
        flash('Application deleted.', 'success')
    except Exception as e:
        if '1451' in str(e):
            flash('Cannot delete: has associated offers. Remove offer first.', 'danger')
        else:
            flash(f'Error: {e}', 'danger')
    return redirect(url_for('applications.index'))
