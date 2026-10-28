"""Offer management routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update, get_db_connection
from config import Config

offer_bp = Blueprint('offers', __name__)


@offer_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    per_page = Config.ITEMS_PER_PAGE
    conditions, params = [], []
    if status_filter:
        conditions.append("o.offer_status = %s"); params.append(status_filter)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    total = execute_query(f"SELECT COUNT(*) AS total FROM offers o {where}",
                          tuple(params) if params else None, fetchone=True)['total']
    offset = (page - 1) * per_page
    offers = execute_query(f"""
        SELECT o.*, s.full_name, s.enrollment_no, jp.job_title, c.company_name
        FROM offers o
        INNER JOIN students s ON s.student_id=o.student_id
        INNER JOIN job_postings jp ON jp.job_id=o.job_id
        INNER JOIN companies c ON c.company_id=o.company_id
        {where} ORDER BY o.offer_date DESC LIMIT %s OFFSET %s""",
        tuple(params + [per_page, offset]))
    total_pages = (total + per_page - 1) // per_page
    return render_template('offers/index.html', offers=offers,
                           page=page, total_pages=total_pages, total=total,
                           status_filter=status_filter)


@offer_bp.route('/add/<int:application_id>', methods=['GET', 'POST'])
def add(application_id):
    app = execute_query("""
        SELECT a.*, s.full_name, s.student_id, s.enrollment_no,
               jp.job_title, jp.job_id, c.company_name, c.company_id
        FROM applications a
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id
        INNER JOIN companies c ON c.company_id=jp.company_id
        WHERE a.application_id=%s""", (application_id,), fetchone=True)
    if not app:
        flash('Application not found.', 'warning')
        return redirect(url_for('applications.index'))
    existing = execute_query("SELECT 1 FROM offers WHERE application_id=%s",
                             (application_id,), fetchone=True)
    if existing:
        flash('An offer already exists for this application.', 'warning')
        return redirect(url_for('applications.view', application_id=application_id))
    if request.method == 'POST':
        offer_date = request.form.get('offer_date', '')
        ctc_lpa = request.form.get('ctc_lpa', type=float)
        offer_status = request.form.get('offer_status', 'Pending')
        joining_date = request.form.get('joining_date', '') or None
        errors = []
        if not offer_date: errors.append('Offer date is required.')
        if not ctc_lpa or ctc_lpa <= 0: errors.append('CTC must be positive.')
        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('offers/form.html', application=app,
                                   offer=request.form, is_edit=False)
        try:
            execute_update("""
                INSERT INTO offers (application_id,student_id,company_id,job_id,
                offer_date,ctc_lpa,offer_status,joining_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (application_id, app['student_id'], app['company_id'], app['job_id'],
                 offer_date, ctc_lpa, offer_status, joining_date))
            flash('Offer created!', 'success')
            return redirect(url_for('applications.view', application_id=application_id))
        except Exception as e:
            if 'accepted offer' in str(e).lower():
                flash('Student already has an accepted offer.', 'danger')
            else:
                flash(f'Error: {e}', 'danger')
    return render_template('offers/form.html', application=app, offer={}, is_edit=False)


@offer_bp.route('/<int:offer_id>/update-status', methods=['POST'])
def update_status(offer_id):
    new_status = request.form.get('offer_status', '').strip()
    if new_status not in ['Pending', 'Accepted', 'Declined']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('offers.index'))
    offer = execute_query("SELECT * FROM offers WHERE offer_id=%s", (offer_id,), fetchone=True)
    if not offer:
        flash('Offer not found.', 'warning')
        return redirect(url_for('offers.index'))
    if new_status == 'Accepted':
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc('sp_process_offer_acceptance', (offer_id,))
                conn.commit()
            flash('Offer accepted! Other pending offers declined.', 'success')
        except Exception as e:
            msg = str(e)
            if 'already has an accepted' in msg.lower():
                flash('Student already has an accepted offer.', 'danger')
            elif 'Only pending' in msg:
                flash('Only pending offers can be accepted.', 'danger')
            else:
                flash(f'Error: {msg}', 'danger')
        finally:
            conn.close()
    else:
        try:
            execute_update("UPDATE offers SET offer_status=%s WHERE offer_id=%s",
                           (new_status, offer_id))
            flash(f'Offer {new_status.lower()}.', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return redirect(url_for('applications.view', application_id=offer['application_id']))
