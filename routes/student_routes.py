"""Student management routes - CRUD operations."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
from services.eligibility_service import get_eligible_jobs_for_student
from config import Config
import re

student_bp = Blueprint('students', __name__)


@student_bp.route('/')
def index():
    """List students with search, filter, and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('department', '', type=str)
    year_filter = request.args.get('year', '', type=str)
    per_page = Config.ITEMS_PER_PAGE

    conditions, params = [], []
    if search:
        conditions.append("(s.full_name LIKE %s OR s.enrollment_no LIKE %s OR s.email LIKE %s)")
        params.extend([f'%{search}%'] * 3)
    if dept_filter:
        conditions.append("s.department_id = %s")
        params.append(dept_filter)
    if year_filter:
        conditions.append("s.graduation_year = %s")
        params.append(year_filter)

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    total = execute_query(
        f"SELECT COUNT(*) AS total FROM students s {where}",
        tuple(params) if params else None, fetchone=True)['total']

    offset = (page - 1) * per_page
    students = execute_query(f"""
        SELECT s.*, d.dept_name, d.dept_code,
               GROUP_CONCAT(DISTINCT sk.skill_name ORDER BY sk.skill_name SEPARATOR ', ') AS skills
        FROM students s
        INNER JOIN departments d ON d.department_id = s.department_id
        LEFT JOIN student_skills ss ON ss.student_id = s.student_id
        LEFT JOIN skills sk ON sk.skill_id = ss.skill_id
        {where}
        GROUP BY s.student_id
        ORDER BY s.full_name
        LIMIT %s OFFSET %s""", tuple(params + [per_page, offset]))

    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    years = execute_query("SELECT DISTINCT graduation_year FROM students ORDER BY graduation_year")
    total_pages = (total + per_page - 1) // per_page

    return render_template('students/index.html',
                           students=students, departments=departments, years=years,
                           page=page, total_pages=total_pages, total=total,
                           search=search, dept_filter=dept_filter, year_filter=year_filter)


@student_bp.route('/add', methods=['GET', 'POST'])
def add():
    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    all_skills = execute_query("SELECT * FROM skills ORDER BY skill_name")

    if request.method == 'POST':
        enrollment_no = request.form.get('enrollment_no', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department_id = request.form.get('department_id', type=int)
        graduation_year = request.form.get('graduation_year', type=int)
        cgpa = request.form.get('cgpa', type=float)
        active_backlogs = request.form.get('active_backlogs', 0, type=int)
        skill_ids = request.form.getlist('skills', type=int)

        errors = validate_student(enrollment_no, full_name, email, department_id,
                                  graduation_year, cgpa, active_backlogs)
        if enrollment_no:
            if execute_query("SELECT 1 FROM students WHERE enrollment_no=%s",
                             (enrollment_no,), fetchone=True):
                errors.append(f'Enrollment number {enrollment_no} already exists.')
        if email:
            if execute_query("SELECT 1 FROM students WHERE email=%s",
                             (email,), fetchone=True):
                errors.append(f'Email {email} is already registered.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('students/form.html', student=request.form,
                                   departments=departments, all_skills=all_skills,
                                   selected_skills=skill_ids, is_edit=False)
        try:
            sid, _ = execute_update(
                """INSERT INTO students (enrollment_no, full_name, email, phone,
                   department_id, graduation_year, cgpa, active_backlogs)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (enrollment_no, full_name, email, phone or None,
                 department_id, graduation_year, cgpa, active_backlogs))
            for sk in skill_ids:
                execute_update("INSERT IGNORE INTO student_skills VALUES (%s,%s)", (sid, sk))
            flash(f'Student {full_name} added successfully!', 'success')
            return redirect(url_for('students.view', student_id=sid))
        except Exception as e:
            flash(f'Error adding student: {e}', 'danger')

    return render_template('students/form.html', student={}, departments=departments,
                           all_skills=all_skills, selected_skills=[], is_edit=False)


@student_bp.route('/<int:student_id>')
def view(student_id):
    student = execute_query("""
        SELECT s.*, d.dept_name, d.dept_code
        FROM students s INNER JOIN departments d ON d.department_id = s.department_id
        WHERE s.student_id = %s""", (student_id,), fetchone=True)
    if not student:
        flash('Student not found.', 'warning')
        return redirect(url_for('students.index'))

    skills = execute_query("""
        SELECT sk.skill_name FROM student_skills ss
        INNER JOIN skills sk ON sk.skill_id = ss.skill_id
        WHERE ss.student_id = %s ORDER BY sk.skill_name""", (student_id,))

    applications = execute_query("""
        SELECT a.*, jp.job_title, jp.job_type, c.company_name, c.company_id
        FROM applications a
        INNER JOIN job_postings jp ON jp.job_id = a.job_id
        INNER JOIN companies c ON c.company_id = jp.company_id
        WHERE a.student_id = %s ORDER BY a.applied_date DESC""", (student_id,))

    interviews = execute_query("""
        SELECT ir.*, jp.job_title, c.company_name
        FROM interview_rounds ir
        INNER JOIN applications a ON a.application_id = ir.application_id
        INNER JOIN job_postings jp ON jp.job_id = a.job_id
        INNER JOIN companies c ON c.company_id = jp.company_id
        WHERE a.student_id = %s ORDER BY ir.scheduled_date DESC""", (student_id,))

    offers = execute_query("""
        SELECT o.*, jp.job_title, c.company_name
        FROM offers o
        INNER JOIN job_postings jp ON jp.job_id = o.job_id
        INNER JOIN companies c ON c.company_id = o.company_id
        WHERE o.student_id = %s ORDER BY o.offer_date DESC""", (student_id,))

    eligible_jobs = get_eligible_jobs_for_student(student_id)

    return render_template('students/view.html', student=student, skills=skills,
                           applications=applications, interviews=interviews,
                           offers=offers, eligible_jobs=eligible_jobs)


@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
def edit(student_id):
    departments = execute_query("SELECT * FROM departments ORDER BY dept_name")
    all_skills = execute_query("SELECT * FROM skills ORDER BY skill_name")
    student = execute_query("SELECT * FROM students WHERE student_id=%s",
                            (student_id,), fetchone=True)
    if not student:
        flash('Student not found.', 'warning')
        return redirect(url_for('students.index'))

    selected_skills = [s['skill_id'] for s in execute_query(
        "SELECT skill_id FROM student_skills WHERE student_id=%s", (student_id,))]

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department_id = request.form.get('department_id', type=int)
        graduation_year = request.form.get('graduation_year', type=int)
        cgpa = request.form.get('cgpa', type=float)
        active_backlogs = request.form.get('active_backlogs', 0, type=int)
        skill_ids = request.form.getlist('skills', type=int)

        errors = validate_student(None, full_name, email, department_id,
                                  graduation_year, cgpa, active_backlogs, skip_enrollment=True)
        if email:
            ex = execute_query("SELECT student_id FROM students WHERE email=%s AND student_id!=%s",
                               (email, student_id), fetchone=True)
            if ex:
                errors.append('Email already registered to another student.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('students/form.html', student=dict(student, **request.form),
                                   departments=departments, all_skills=all_skills,
                                   selected_skills=skill_ids, is_edit=True)
        try:
            execute_update(
                """UPDATE students SET full_name=%s, email=%s, phone=%s,
                   department_id=%s, graduation_year=%s, cgpa=%s, active_backlogs=%s
                   WHERE student_id=%s""",
                (full_name, email, phone or None, department_id,
                 graduation_year, cgpa, active_backlogs, student_id))
            execute_update("DELETE FROM student_skills WHERE student_id=%s", (student_id,))
            for sk in skill_ids:
                execute_update("INSERT INTO student_skills VALUES (%s,%s)", (student_id, sk))
            flash(f'Student {full_name} updated successfully!', 'success')
            return redirect(url_for('students.view', student_id=student_id))
        except Exception as e:
            flash(f'Error updating student: {e}', 'danger')

    return render_template('students/form.html', student=student, departments=departments,
                           all_skills=all_skills, selected_skills=selected_skills, is_edit=True)


@student_bp.route('/<int:student_id>/delete', methods=['POST'])
def delete(student_id):
    try:
        execute_update("DELETE FROM students WHERE student_id=%s", (student_id,))
        flash('Student deleted successfully.', 'success')
    except Exception as e:
        if '1451' in str(e) or 'foreign key' in str(e).lower():
            flash('Cannot delete: student has existing applications or offers.', 'danger')
        else:
            flash(f'Error: {e}', 'danger')
    return redirect(url_for('students.index'))


def validate_student(enrollment_no, full_name, email, department_id,
                     graduation_year, cgpa, active_backlogs, skip_enrollment=False):
    errors = []
    if not skip_enrollment and not enrollment_no:
        errors.append('Enrollment number is required.')
    if not full_name:
        errors.append('Full name is required.')
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Valid email is required.')
    if not department_id:
        errors.append('Department is required.')
    if not graduation_year or graduation_year < 2020 or graduation_year > 2035:
        errors.append('Valid graduation year (2020-2035) is required.')
    if cgpa is None or cgpa < 0 or cgpa > 10:
        errors.append('CGPA must be between 0 and 10.')
    if active_backlogs is not None and active_backlogs < 0:
        errors.append('Active backlogs cannot be negative.')
    return errors
