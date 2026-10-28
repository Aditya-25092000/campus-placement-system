"""Job posting management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
from config import Config

job_bp = Blueprint('jobs', __name__)


@job_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    company_filter = request.args.get('company', '', type=str)
    per_page = Config.ITEMS_PER_PAGE
    conditions, params = [], []
    if search:
        conditions.append("(jp.job_title LIKE %s OR c.company_name LIKE %s)")
        params.extend([f'%{search}%', f'%{search}%'])
    if status_filter:
        conditions.append("jp.status = %s"); params.append(status_filter)
    if company_filter:
        conditions.append("jp.company_id = %s"); params.append(company_filter)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    total = execute_query(
        f"SELECT COUNT(*) AS total FROM job_postings jp INNER JOIN companies c ON c.company_id=jp.company_id {where}",
        tuple(params) if params else None, fetchone=True)['total']
    offset = (page - 1) * per_page
    jobs = execute_query(f"""
        SELECT jp.*, c.company_name, COUNT(DISTINCT a.application_id) AS app_count,
               COUNT(DISTINCT jad.department_id) AS dept_count
        FROM job_postings jp
        INNER JOIN companies c ON c.company_id = jp.company_id
        LEFT JOIN applications a ON a.job_id = jp.job_id
        LEFT JOIN job_allowed_departments jad ON jad.job_id = jp.job_id
        {where}
        GROUP BY jp.job_id ORDER BY jp.created_at DESC
        LIMIT %s OFFSET %s""", tuple(params + [per_page, offset]))
    companies = execute_query("SELECT company_id, company_name FROM companies ORDER BY company_name")
    total_pages = (total + per_page - 1) // per_page
    return render_template('jobs/index.html', jobs=jobs, companies=companies,
                           page=page, total_pages=total_pages, total=total,
                           search=search, status_filter=status_filter, company_filter=company_filter)


@job_bp.route('/add', methods=['GET', 'POST'])
def add():
    companies = execute_query("SELECT * FROM companies ORDER BY company_name")
    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    all_skills = execute_query("SELECT * FROM skills ORDER BY skill_name")
    if request.method == 'POST':
        return _save_job(None, companies, departments, all_skills)
    return render_template('jobs/form.html', job={}, companies=companies,
                           departments=departments, all_skills=all_skills,
                           selected_depts=[], selected_skills=[], is_edit=False)


@job_bp.route('/<int:job_id>')
def view(job_id):
    job = execute_query("""
        SELECT jp.*, c.company_name FROM job_postings jp
        INNER JOIN companies c ON c.company_id = jp.company_id
        WHERE jp.job_id = %s""", (job_id,), fetchone=True)
    if not job:
        flash('Job not found.', 'warning')
        return redirect(url_for('jobs.index'))
    departments = execute_query("""
        SELECT d.* FROM job_allowed_departments jad
        INNER JOIN departments d ON d.department_id = jad.department_id
        WHERE jad.job_id = %s ORDER BY d.dept_name""", (job_id,))
    skills = execute_query("""
        SELECT sk.* FROM job_required_skills jrs
        INNER JOIN skills sk ON sk.skill_id = jrs.skill_id
        WHERE jrs.job_id = %s ORDER BY sk.skill_name""", (job_id,))
    applications = execute_query("""
        SELECT a.*, s.full_name, s.enrollment_no, d.dept_name
        FROM applications a
        INNER JOIN students s ON s.student_id = a.student_id
        INNER JOIN departments d ON d.department_id = s.department_id
        WHERE a.job_id = %s ORDER BY a.applied_date DESC""", (job_id,))
    return render_template('jobs/view.html', job=job, departments=departments,
                           skills=skills, applications=applications)


@job_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
def edit(job_id):
    companies = execute_query("SELECT * FROM companies ORDER BY company_name")
    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    all_skills = execute_query("SELECT * FROM skills ORDER BY skill_name")
    job = execute_query("SELECT * FROM job_postings WHERE job_id=%s", (job_id,), fetchone=True)
    if not job:
        flash('Job not found.', 'warning')
        return redirect(url_for('jobs.index'))
    if request.method == 'POST':
        return _save_job(job_id, companies, departments, all_skills)
    sel_depts = [d['department_id'] for d in execute_query(
        "SELECT department_id FROM job_allowed_departments WHERE job_id=%s", (job_id,))]
    sel_skills = [s['skill_id'] for s in execute_query(
        "SELECT skill_id FROM job_required_skills WHERE job_id=%s", (job_id,))]
    return render_template('jobs/form.html', job=job, companies=companies,
                           departments=departments, all_skills=all_skills,
                           selected_depts=sel_depts, selected_skills=sel_skills, is_edit=True)


@job_bp.route('/<int:job_id>/delete', methods=['POST'])
def delete(job_id):
    try:
        execute_update("DELETE FROM job_postings WHERE job_id=%s", (job_id,))
        flash('Job posting deleted.', 'success')
    except Exception as e:
        if '1451' in str(e) or 'foreign key' in str(e).lower():
            flash('Cannot delete: job has existing applications.', 'danger')
        else:
            flash(f'Error: {e}', 'danger')
    return redirect(url_for('jobs.index'))


def _save_job(job_id, companies, departments, all_skills):
    """Shared create/update logic."""
    company_id = request.form.get('company_id', type=int)
    job_title = request.form.get('job_title', '').strip()
    job_description = request.form.get('job_description', '').strip()
    job_location = request.form.get('job_location', '').strip()
    job_type = request.form.get('job_type', 'Full-time')
    min_cgpa = request.form.get('min_cgpa', 0, type=float)
    max_backlogs = request.form.get('max_backlogs', 0, type=int)
    eligible_grad_year = request.form.get('eligible_grad_year', type=int)
    open_date = request.form.get('application_open_date', '')
    deadline = request.form.get('application_deadline', '')
    status = request.form.get('status', 'Active')
    dept_ids = request.form.getlist('departments', type=int)
    skill_ids = request.form.getlist('skills', type=int)
    is_edit = job_id is not None

    errors = []
    if not company_id: errors.append('Company is required.')
    if not job_title: errors.append('Job title is required.')
    if not open_date: errors.append('Open date is required.')
    if not deadline: errors.append('Deadline is required.')
    if errors:
        for e in errors:
            flash(e, 'danger')
        return render_template('jobs/form.html', job=request.form, companies=companies,
                               departments=departments, all_skills=all_skills,
                               selected_depts=dept_ids, selected_skills=skill_ids, is_edit=is_edit)
    try:
        if is_edit:
            execute_update("""
                UPDATE job_postings SET company_id=%s,job_title=%s,job_description=%s,
                job_location=%s,job_type=%s,min_cgpa=%s,max_backlogs=%s,eligible_grad_year=%s,
                application_open_date=%s,application_deadline=%s,status=%s WHERE job_id=%s""",
                (company_id, job_title, job_description or None, job_location or None,
                 job_type, min_cgpa, max_backlogs, eligible_grad_year or None,
                 open_date, deadline, status, job_id))
            execute_update("DELETE FROM job_allowed_departments WHERE job_id=%s", (job_id,))
            execute_update("DELETE FROM job_required_skills WHERE job_id=%s", (job_id,))
        else:
            job_id, _ = execute_update("""
                INSERT INTO job_postings (company_id,job_title,job_description,job_location,
                job_type,min_cgpa,max_backlogs,eligible_grad_year,
                application_open_date,application_deadline,status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (company_id, job_title, job_description or None, job_location or None,
                 job_type, min_cgpa, max_backlogs, eligible_grad_year or None,
                 open_date, deadline, status))
        for did in dept_ids:
            execute_update("INSERT IGNORE INTO job_allowed_departments VALUES (%s,%s)", (job_id, did))
        for sid in skill_ids:
            execute_update("INSERT IGNORE INTO job_required_skills VALUES (%s,%s)", (job_id, sid))
        flash(f'Job "{job_title}" {"updated" if is_edit else "created"}!', 'success')
        return redirect(url_for('jobs.view', job_id=job_id))
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('jobs/form.html', job=request.form, companies=companies,
                               departments=departments, all_skills=all_skills,
                               selected_depts=dept_ids, selected_skills=skill_ids, is_edit=is_edit)
