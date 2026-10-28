"""Interview round management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update

interview_bp = Blueprint('interviews', __name__)


@interview_bp.route('/add/<int:application_id>', methods=['GET', 'POST'])
def add(application_id):
    app = execute_query("""
        SELECT a.*, s.full_name, jp.job_title, c.company_name
        FROM applications a
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id
        INNER JOIN companies c ON c.company_id=jp.company_id
        WHERE a.application_id=%s""", (application_id,), fetchone=True)
    if not app:
        flash('Application not found.', 'warning')
        return redirect(url_for('applications.index'))
    if request.method == 'POST':
        round_name = request.form.get('round_name', '').strip()
        scheduled_date = request.form.get('scheduled_date', '')
        mode = request.form.get('interview_mode', 'In-Person')
        location = request.form.get('location_details', '').strip()
        if not round_name or not scheduled_date:
            flash('Round name and date are required.', 'danger')
            return render_template('interviews/form.html', application=app,
                                   interview=request.form, is_edit=False)
        try:
            execute_update("""
                INSERT INTO interview_rounds (application_id,round_name,scheduled_date,
                interview_mode,location_details) VALUES (%s,%s,%s,%s,%s)""",
                (application_id, round_name, scheduled_date, mode, location or None))
            flash(f'{round_name} round scheduled!', 'success')
            return redirect(url_for('applications.view', application_id=application_id))
        except Exception as e:
            if 'Duplicate' in str(e) or 'unique_app_round' in str(e).lower():
                flash(f'A "{round_name}" round already exists for this application.', 'danger')
            else:
                flash(f'Error: {e}', 'danger')
    return render_template('interviews/form.html', application=app, interview={}, is_edit=False)


@interview_bp.route('/<int:interview_id>/edit', methods=['GET', 'POST'])
def edit(interview_id):
    interview = execute_query("""
        SELECT ir.*, a.application_id, s.full_name, jp.job_title, c.company_name
        FROM interview_rounds ir
        INNER JOIN applications a ON a.application_id=ir.application_id
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id
        INNER JOIN companies c ON c.company_id=jp.company_id
        WHERE ir.interview_id=%s""", (interview_id,), fetchone=True)
    if not interview:
        flash('Interview not found.', 'warning')
        return redirect(url_for('applications.index'))
    if request.method == 'POST':
        try:
            execute_update("""
                UPDATE interview_rounds SET scheduled_date=%s, interview_mode=%s,
                location_details=%s, status=%s, result=%s, feedback=%s
                WHERE interview_id=%s""",
                (request.form.get('scheduled_date'),
                 request.form.get('interview_mode', 'In-Person'),
                 request.form.get('location_details') or None,
                 request.form.get('status', 'Scheduled'),
                 request.form.get('result', 'Pending'),
                 request.form.get('feedback') or None, interview_id))
            flash('Interview updated!', 'success')
            return redirect(url_for('applications.view',
                                    application_id=interview['application_id']))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('interviews/form.html', application=interview,
                           interview=interview, is_edit=True)


@interview_bp.route('/<int:interview_id>/delete', methods=['POST'])
def delete(interview_id):
    iv = execute_query("SELECT application_id FROM interview_rounds WHERE interview_id=%s",
                       (interview_id,), fetchone=True)
    if not iv:
        flash('Not found.', 'warning')
        return redirect(url_for('applications.index'))
    execute_update("DELETE FROM interview_rounds WHERE interview_id=%s", (interview_id,))
    flash('Interview round deleted.', 'success')
    return redirect(url_for('applications.view', application_id=iv['application_id']))
