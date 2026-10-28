"""Company management routes - CRUD operations."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
from config import Config

company_bp = Blueprint('companies', __name__)


@company_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = Config.ITEMS_PER_PAGE
    conditions, params = [], []
    if search:
        conditions.append("(c.company_name LIKE %s OR c.industry LIKE %s)")
        params.extend([f'%{search}%', f'%{search}%'])
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    total = execute_query(f"SELECT COUNT(*) AS total FROM companies c {where}",
                          tuple(params) if params else None, fetchone=True)['total']
    offset = (page - 1) * per_page
    companies = execute_query(f"""
        SELECT c.*, COUNT(DISTINCT jp.job_id) AS job_count,
               COUNT(DISTINCT a.application_id) AS app_count
        FROM companies c
        LEFT JOIN job_postings jp ON jp.company_id = c.company_id
        LEFT JOIN applications a ON a.job_id = jp.job_id
        {where}
        GROUP BY c.company_id ORDER BY c.company_name
        LIMIT %s OFFSET %s""", tuple(params + [per_page, offset]))
    total_pages = (total + per_page - 1) // per_page
    return render_template('companies/index.html', companies=companies,
                           page=page, total_pages=total_pages, total=total, search=search)


@company_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('company_name', '').strip()
        if not name:
            flash('Company name is required.', 'danger')
            return render_template('companies/form.html', company=request.form, is_edit=False)
        if execute_query("SELECT 1 FROM companies WHERE company_name=%s", (name,), fetchone=True):
            flash(f'Company "{name}" already exists.', 'danger')
            return render_template('companies/form.html', company=request.form, is_edit=False)
        try:
            cid, _ = execute_update(
                """INSERT INTO companies (company_name,industry,website,
                   hr_contact_name,hr_email,contact_number,description)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (name, request.form.get('industry') or None,
                 request.form.get('website') or None,
                 request.form.get('hr_contact_name') or None,
                 request.form.get('hr_email') or None,
                 request.form.get('contact_number') or None,
                 request.form.get('description') or None))
            flash(f'Company {name} added!', 'success')
            return redirect(url_for('companies.view', company_id=cid))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('companies/form.html', company={}, is_edit=False)


@company_bp.route('/<int:company_id>')
def view(company_id):
    company = execute_query("SELECT * FROM companies WHERE company_id=%s",
                            (company_id,), fetchone=True)
    if not company:
        flash('Company not found.', 'warning')
        return redirect(url_for('companies.index'))
    jobs = execute_query("""
        SELECT jp.*, COUNT(a.application_id) AS app_count
        FROM job_postings jp LEFT JOIN applications a ON a.job_id = jp.job_id
        WHERE jp.company_id = %s GROUP BY jp.job_id ORDER BY jp.created_at DESC""",
        (company_id,))
    return render_template('companies/view.html', company=company, jobs=jobs)


@company_bp.route('/<int:company_id>/edit', methods=['GET', 'POST'])
def edit(company_id):
    company = execute_query("SELECT * FROM companies WHERE company_id=%s",
                            (company_id,), fetchone=True)
    if not company:
        flash('Company not found.', 'warning')
        return redirect(url_for('companies.index'))
    if request.method == 'POST':
        name = request.form.get('company_name', '').strip()
        if not name:
            flash('Company name is required.', 'danger')
            return render_template('companies/form.html', company=request.form, is_edit=True)
        ex = execute_query("SELECT company_id FROM companies WHERE company_name=%s AND company_id!=%s",
                           (name, company_id), fetchone=True)
        if ex:
            flash(f'Name "{name}" already taken.', 'danger')
            return render_template('companies/form.html', company=request.form, is_edit=True)
        try:
            execute_update(
                """UPDATE companies SET company_name=%s,industry=%s,website=%s,
                   hr_contact_name=%s,hr_email=%s,contact_number=%s,description=%s
                   WHERE company_id=%s""",
                (name, request.form.get('industry') or None,
                 request.form.get('website') or None,
                 request.form.get('hr_contact_name') or None,
                 request.form.get('hr_email') or None,
                 request.form.get('contact_number') or None,
                 request.form.get('description') or None, company_id))
            flash(f'Company {name} updated!', 'success')
            return redirect(url_for('companies.view', company_id=company_id))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('companies/form.html', company=company, is_edit=True)


@company_bp.route('/<int:company_id>/delete', methods=['POST'])
def delete(company_id):
    try:
        execute_update("DELETE FROM companies WHERE company_id=%s", (company_id,))
        flash('Company deleted.', 'success')
    except Exception as e:
        if '1451' in str(e) or 'foreign key' in str(e).lower():
            flash('Cannot delete: company has existing job postings.', 'danger')
        else:
            flash(f'Error: {e}', 'danger')
    return redirect(url_for('companies.index'))
