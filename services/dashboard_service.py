"""Dashboard statistics service — all metrics from real MySQL queries."""
from db import execute_query


def get_dashboard_stats():
    """Fetch all dashboard KPI metrics."""
    stats = {}
    r = execute_query("SELECT COUNT(*) AS c FROM students", fetchone=True)
    stats['total_students'] = r['c']
    r = execute_query("SELECT COUNT(*) AS c FROM companies", fetchone=True)
    stats['total_companies'] = r['c']
    r = execute_query("SELECT COUNT(*) AS c FROM job_postings WHERE status = 'Active'", fetchone=True)
    stats['active_jobs'] = r['c']
    r = execute_query("SELECT COUNT(*) AS c FROM applications", fetchone=True)
    stats['total_applications'] = r['c']
    r = execute_query(
        "SELECT COUNT(DISTINCT student_id) AS c FROM offers WHERE offer_status = 'Accepted'",
        fetchone=True)
    stats['students_placed'] = r['c']
    r = execute_query("""
        SELECT COUNT(DISTINCT s.student_id) AS c
        FROM students s
        WHERE EXISTS (
            SELECT 1 FROM job_postings jp
            INNER JOIN job_allowed_departments jad
                ON jad.job_id = jp.job_id AND jad.department_id = s.department_id
            WHERE jp.status = 'Active'
              AND jp.application_deadline >= CURDATE()
              AND s.cgpa >= jp.min_cgpa
              AND s.active_backlogs <= jp.max_backlogs
              AND (jp.eligible_grad_year IS NULL OR s.graduation_year = jp.eligible_grad_year)
        )""", fetchone=True)
    stats['eligible_students'] = r['c']
    return stats


def get_application_status_chart():
    """Get application counts by status for chart."""
    return execute_query(
        """SELECT status, COUNT(*) AS count FROM applications
           GROUP BY status
           ORDER BY FIELD(status,'Applied','Shortlisted','Interview','Selected','Rejected','Withdrawn')""")


def get_department_placement_chart():
    """Get department-wise placement data for chart."""
    return execute_query("""
        SELECT d.dept_name,
               COUNT(DISTINCT s.student_id) AS total,
               COUNT(DISTINCT CASE WHEN o.offer_status = 'Accepted' THEN s.student_id END) AS placed
        FROM departments d
        LEFT JOIN students s ON s.department_id = d.department_id
        LEFT JOIN applications a ON a.student_id = s.student_id
        LEFT JOIN offers o ON o.application_id = a.application_id
        GROUP BY d.department_id, d.dept_name
        ORDER BY d.dept_name""")


def get_recent_applications(limit=5):
    """Get most recent applications."""
    return execute_query("""
        SELECT a.application_id, s.full_name, s.enrollment_no,
               d.dept_name, jp.job_title, c.company_name,
               a.status, a.applied_date
        FROM applications a
        INNER JOIN students s ON s.student_id = a.student_id
        INNER JOIN departments d ON d.department_id = s.department_id
        INNER JOIN job_postings jp ON jp.job_id = a.job_id
        INNER JOIN companies c ON c.company_id = jp.company_id
        ORDER BY a.applied_date DESC LIMIT %s""", (limit,))


def get_upcoming_interviews(limit=5):
    """Get upcoming scheduled interviews."""
    return execute_query("""
        SELECT ir.interview_id, ir.round_name, ir.scheduled_date,
               ir.interview_mode, ir.location_details,
               s.full_name, s.enrollment_no,
               jp.job_title, c.company_name
        FROM interview_rounds ir
        INNER JOIN applications a ON a.application_id = ir.application_id
        INNER JOIN students s ON s.student_id = a.student_id
        INNER JOIN job_postings jp ON jp.job_id = a.job_id
        INNER JOIN companies c ON c.company_id = jp.company_id
        WHERE ir.status = 'Scheduled' AND ir.scheduled_date >= NOW()
        ORDER BY ir.scheduled_date ASC LIMIT %s""", (limit,))
