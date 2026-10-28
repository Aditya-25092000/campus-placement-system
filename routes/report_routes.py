"""Reports routes with CSV export."""
from flask import Blueprint, render_template, Response
from db import execute_query
import csv, io

report_bp = Blueprint('reports', __name__)


@report_bp.route('/')
def index():
    dept_stats = execute_query("""
        SELECT d.dept_name, COUNT(DISTINCT s.student_id) AS total_students,
               COUNT(DISTINCT CASE WHEN a.application_id IS NOT NULL THEN s.student_id END) AS applied,
               COUNT(DISTINCT CASE WHEN o.offer_status='Accepted' THEN s.student_id END) AS placed,
               ROUND(AVG(CASE WHEN o.offer_status='Accepted' THEN o.ctc_lpa END),2) AS avg_ctc
        FROM departments d
        LEFT JOIN students s ON s.department_id=d.department_id
        LEFT JOIN applications a ON a.student_id=s.student_id
        LEFT JOIN offers o ON o.application_id=a.application_id
        GROUP BY d.department_id,d.dept_name ORDER BY d.dept_name""")

    company_stats = execute_query("""
        SELECT c.company_name, COUNT(a.application_id) AS app_count,
               COUNT(CASE WHEN a.status='Selected' THEN 1 END) AS selected,
               COUNT(DISTINCT jp.job_id) AS job_count
        FROM companies c
        LEFT JOIN job_postings jp ON jp.company_id=c.company_id
        LEFT JOIN applications a ON a.job_id=jp.job_id
        GROUP BY c.company_id,c.company_name ORDER BY app_count DESC""")

    status_dist = execute_query("""
        SELECT status, COUNT(*) AS count FROM applications GROUP BY status
        ORDER BY FIELD(status,'Applied','Shortlisted','Interview','Selected','Rejected','Withdrawn')""")

    no_apps = execute_query("""
        SELECT s.student_id, s.enrollment_no, s.full_name, d.dept_name, s.cgpa
        FROM students s INNER JOIN departments d ON d.department_id=s.department_id
        LEFT JOIN applications a ON a.student_id=s.student_id
        WHERE a.application_id IS NULL ORDER BY s.full_name""")

    placed = execute_query("""
        SELECT s.full_name, s.enrollment_no, d.dept_name,
               c.company_name, jp.job_title, o.ctc_lpa, o.joining_date
        FROM offers o
        INNER JOIN students s ON s.student_id=o.student_id
        INNER JOIN departments d ON d.department_id=s.department_id
        INNER JOIN companies c ON c.company_id=o.company_id
        INNER JOIN job_postings jp ON jp.job_id=o.job_id
        WHERE o.offer_status='Accepted' ORDER BY o.offer_date DESC""")

    recent = execute_query("""
        SELECT s.full_name, s.enrollment_no, d.dept_name,
               c.company_name, jp.job_title, a.status AS app_status, a.updated_at
        FROM applications a
        INNER JOIN students s ON s.student_id=a.student_id
        INNER JOIN departments d ON d.department_id=s.department_id
        INNER JOIN job_postings jp ON jp.job_id=a.job_id
        INNER JOIN companies c ON c.company_id=jp.company_id
        ORDER BY a.updated_at DESC LIMIT 10""")

    return render_template('reports/index.html', dept_stats=dept_stats,
                           company_stats=company_stats, status_dist=status_dist,
                           no_apps=no_apps, placed=placed, recent=recent)


@report_bp.route('/export/<report_type>')
def export_csv(report_type):
    output = io.StringIO()
    writer = csv.writer(output)
    if report_type == 'department':
        writer.writerow(['Department','Total Students','Applied','Placed','Avg CTC (LPA)'])
        for r in execute_query("""
            SELECT d.dept_name, COUNT(DISTINCT s.student_id) AS total,
                   COUNT(DISTINCT CASE WHEN a.application_id IS NOT NULL THEN s.student_id END) AS applied,
                   COUNT(DISTINCT CASE WHEN o.offer_status='Accepted' THEN s.student_id END) AS placed,
                   ROUND(AVG(CASE WHEN o.offer_status='Accepted' THEN o.ctc_lpa END),2) AS avg_ctc
            FROM departments d LEFT JOIN students s ON s.department_id=d.department_id
            LEFT JOIN applications a ON a.student_id=s.student_id
            LEFT JOIN offers o ON o.application_id=a.application_id
            GROUP BY d.department_id,d.dept_name ORDER BY d.dept_name"""):
            writer.writerow([r['dept_name'],r['total'],r['applied'],r['placed'],r['avg_ctc'] or 'N/A'])
    elif report_type == 'placed':
        writer.writerow(['Student','Enrollment','Department','Company','Job','CTC (LPA)','Joining Date'])
        for r in execute_query("""
            SELECT s.full_name, s.enrollment_no, d.dept_name, c.company_name,
                   jp.job_title, o.ctc_lpa, o.joining_date
            FROM offers o INNER JOIN students s ON s.student_id=o.student_id
            INNER JOIN departments d ON d.department_id=s.department_id
            INNER JOIN companies c ON c.company_id=o.company_id
            INNER JOIN job_postings jp ON jp.job_id=o.job_id
            WHERE o.offer_status='Accepted' ORDER BY s.full_name"""):
            writer.writerow([r['full_name'],r['enrollment_no'],r['dept_name'],
                           r['company_name'],r['job_title'],r['ctc_lpa'],r['joining_date'] or 'TBD'])
    elif report_type == 'no_applications':
        writer.writerow(['Student','Enrollment','Department','CGPA'])
        for r in execute_query("""
            SELECT s.full_name, s.enrollment_no, d.dept_name, s.cgpa
            FROM students s INNER JOIN departments d ON d.department_id=s.department_id
            LEFT JOIN applications a ON a.student_id=s.student_id
            WHERE a.application_id IS NULL ORDER BY s.full_name"""):
            writer.writerow([r['full_name'],r['enrollment_no'],r['dept_name'],r['cgpa']])
    elif report_type == 'company':
        writer.writerow(['Company','Job Postings','Applications','Selected'])
        for r in execute_query("""
            SELECT c.company_name, COUNT(DISTINCT jp.job_id) AS jobs,
                   COUNT(a.application_id) AS apps,
                   COUNT(CASE WHEN a.status='Selected' THEN 1 END) AS selected
            FROM companies c LEFT JOIN job_postings jp ON jp.company_id=c.company_id
            LEFT JOIN applications a ON a.job_id=jp.job_id
            GROUP BY c.company_id,c.company_name ORDER BY c.company_name"""):
            writer.writerow([r['company_name'],r['jobs'],r['apps'],r['selected']])
    else:
        return "Invalid report type", 404
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename={report_type}_report.csv'})
