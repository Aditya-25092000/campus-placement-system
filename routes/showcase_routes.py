"""SQL Showcase routes - demonstrates DBMS concepts for viva."""
from flask import Blueprint, render_template
from db import execute_query, get_db_connection, call_procedure

showcase_bp = Blueprint('showcase', __name__)


@showcase_bp.route('/')
def index():
    demos = []

    # 1. INNER JOIN
    demos.append({
        'title': '1. INNER JOIN — Students with Departments',
        'sql': "SELECT s.enrollment_no, s.full_name, s.cgpa,\n       d.dept_name, d.dept_code\nFROM students s\nINNER JOIN departments d\n    ON d.department_id = s.department_id\nORDER BY d.dept_name, s.full_name\nLIMIT 15;",
        'explanation': 'INNER JOIN returns only rows where there is a matching record in both tables. Here it links each student to their department.',
        'results': execute_query(
            "SELECT s.enrollment_no, s.full_name, s.cgpa, d.dept_name, d.dept_code "
            "FROM students s INNER JOIN departments d ON d.department_id=s.department_id "
            "ORDER BY d.dept_name, s.full_name LIMIT 15")
    })

    # 2. LEFT JOIN
    demos.append({
        'title': '2. LEFT JOIN — Students Who Never Applied',
        'sql': "SELECT s.enrollment_no, s.full_name,\n       d.dept_name, s.cgpa\nFROM students s\nINNER JOIN departments d ON d.department_id = s.department_id\nLEFT JOIN applications a ON a.student_id = s.student_id\nWHERE a.application_id IS NULL\nORDER BY s.full_name;",
        'explanation': 'LEFT JOIN returns all rows from the left table even without a match. WHERE IS NULL finds students with zero applications.',
        'results': execute_query(
            "SELECT s.enrollment_no, s.full_name, d.dept_name, s.cgpa "
            "FROM students s INNER JOIN departments d ON d.department_id=s.department_id "
            "LEFT JOIN applications a ON a.student_id=s.student_id "
            "WHERE a.application_id IS NULL ORDER BY s.full_name")
    })

    # 3. GROUP BY
    demos.append({
        'title': '3. GROUP BY — Department-wise Placement Statistics',
        'sql': "SELECT d.dept_name,\n       COUNT(DISTINCT s.student_id) AS total_students,\n       COUNT(DISTINCT CASE\n           WHEN o.offer_status = 'Accepted'\n           THEN s.student_id END) AS placed,\n       ROUND(AVG(CASE\n           WHEN o.offer_status = 'Accepted'\n           THEN o.ctc_lpa END), 2) AS avg_ctc\nFROM departments d\nLEFT JOIN students s ON s.department_id = d.department_id\nLEFT JOIN applications a ON a.student_id = s.student_id\nLEFT JOIN offers o ON o.application_id = a.application_id\nGROUP BY d.department_id, d.dept_name;",
        'explanation': 'GROUP BY aggregates rows with common values. With COUNT, AVG, and CASE, it calculates per-department placement statistics.',
        'results': execute_query(
            "SELECT d.dept_name, COUNT(DISTINCT s.student_id) AS total_students, "
            "COUNT(DISTINCT CASE WHEN o.offer_status='Accepted' THEN s.student_id END) AS placed, "
            "ROUND(AVG(CASE WHEN o.offer_status='Accepted' THEN o.ctc_lpa END),2) AS avg_ctc "
            "FROM departments d LEFT JOIN students s ON s.department_id=d.department_id "
            "LEFT JOIN applications a ON a.student_id=s.student_id "
            "LEFT JOIN offers o ON o.application_id=a.application_id "
            "GROUP BY d.department_id, d.dept_name ORDER BY d.dept_name")
    })

    # 4. Subquery
    demos.append({
        'title': '4. Subquery — Students with CGPA Above Department Average',
        'sql': "SELECT s.enrollment_no, s.full_name,\n       d.dept_name, s.cgpa,\n       dept_avg.avg_cgpa AS dept_average\nFROM students s\nINNER JOIN departments d ON d.department_id = s.department_id\nINNER JOIN (\n    SELECT department_id, ROUND(AVG(cgpa), 2) AS avg_cgpa\n    FROM students GROUP BY department_id\n) dept_avg ON dept_avg.department_id = s.department_id\nWHERE s.cgpa > dept_avg.avg_cgpa\nORDER BY d.dept_name, s.cgpa DESC;",
        'explanation': 'A subquery (derived table) calculates each department\'s average CGPA. The outer query selects students exceeding their department\'s average.',
        'results': execute_query(
            "SELECT s.enrollment_no, s.full_name, d.dept_name, s.cgpa, "
            "dept_avg.avg_cgpa AS dept_average "
            "FROM students s INNER JOIN departments d ON d.department_id=s.department_id "
            "INNER JOIN (SELECT department_id, ROUND(AVG(cgpa),2) AS avg_cgpa FROM students GROUP BY department_id) "
            "dept_avg ON dept_avg.department_id=s.department_id "
            "WHERE s.cgpa > dept_avg.avg_cgpa ORDER BY d.dept_name, s.cgpa DESC")
    })

    # 5. Aggregate
    demos.append({
        'title': '5. Aggregate — Company Application Counts',
        'sql': "SELECT c.company_name, c.industry,\n       COUNT(a.application_id) AS total_applications,\n       COUNT(DISTINCT a.student_id) AS unique_applicants\nFROM companies c\nINNER JOIN job_postings jp ON jp.company_id = c.company_id\nLEFT JOIN applications a ON a.job_id = jp.job_id\nGROUP BY c.company_id, c.company_name, c.industry\nORDER BY total_applications DESC;",
        'explanation': 'Aggregate functions (COUNT) with GROUP BY calculate company-level metrics. ORDER BY DESC finds the company with most applications.',
        'results': execute_query(
            "SELECT c.company_name, c.industry, COUNT(a.application_id) AS total_applications, "
            "COUNT(DISTINCT a.student_id) AS unique_applicants "
            "FROM companies c INNER JOIN job_postings jp ON jp.company_id=c.company_id "
            "LEFT JOIN applications a ON a.job_id=jp.job_id "
            "GROUP BY c.company_id, c.company_name, c.industry ORDER BY total_applications DESC")
    })

    # 6. Eligibility query
    fj = execute_query("SELECT job_id, job_title FROM job_postings WHERE status='Active' LIMIT 1", fetchone=True)
    jid = fj['job_id'] if fj else 1
    jt = fj['job_title'] if fj else 'N/A'
    demos.append({
        'title': f'6. Eligibility Query — Candidates for "{jt}"',
        'sql': f"SELECT s.enrollment_no, s.full_name,\n       d.dept_name, s.cgpa, s.active_backlogs,\n       GROUP_CONCAT(sk.skill_name SEPARATOR ', ') AS skills\nFROM students s\nINNER JOIN departments d ON d.department_id = s.department_id\nINNER JOIN job_allowed_departments jad\n    ON jad.department_id = s.department_id AND jad.job_id = {jid}\nLEFT JOIN student_skills ss ON ss.student_id = s.student_id\nLEFT JOIN skills sk ON sk.skill_id = ss.skill_id\nWHERE s.cgpa >= (SELECT min_cgpa FROM job_postings WHERE job_id = {jid})\n  AND s.active_backlogs <= (SELECT max_backlogs FROM job_postings WHERE job_id = {jid})\nGROUP BY s.student_id\nORDER BY s.cgpa DESC;",
        'explanation': 'Combines INNER JOIN (department check), subqueries (CGPA/backlog thresholds), and GROUP_CONCAT to find eligible candidates.',
        'results': execute_query(
            "SELECT s.enrollment_no, s.full_name, d.dept_name, s.cgpa, s.active_backlogs, "
            "GROUP_CONCAT(sk.skill_name SEPARATOR ', ') AS skills "
            "FROM students s INNER JOIN departments d ON d.department_id=s.department_id "
            "INNER JOIN job_allowed_departments jad ON jad.department_id=s.department_id AND jad.job_id=%s "
            "LEFT JOIN student_skills ss ON ss.student_id=s.student_id "
            "LEFT JOIN skills sk ON sk.skill_id=ss.skill_id "
            "WHERE s.cgpa>=(SELECT min_cgpa FROM job_postings WHERE job_id=%s) "
            "AND s.active_backlogs<=(SELECT max_backlogs FROM job_postings WHERE job_id=%s) "
            "GROUP BY s.student_id ORDER BY s.cgpa DESC", (jid, jid, jid))
    })

    # 7. View
    demos.append({
        'title': '7. View — Placement Summary (vw_placement_summary)',
        'sql': "-- Pre-defined MySQL VIEW:\nSELECT * FROM vw_placement_summary;",
        'explanation': 'A VIEW is a virtual table defined by a stored SELECT. vw_placement_summary joins departments, students, applications, and offers for an always-current overview.',
        'results': execute_query("SELECT * FROM vw_placement_summary")
    })

    # 8. Stored procedure
    demos.append({
        'title': '8. Stored Procedure — sp_department_placement_summary()',
        'sql': "CALL sp_department_placement_summary();\n\n-- Encapsulates complex logic on the server.\n-- Can accept parameters and use variables.",
        'explanation': 'A Stored Procedure encapsulates complex SQL on the database server. This one generates a comprehensive department-wise placement summary.',
        'results': call_procedure('sp_department_placement_summary')
    })

    # 9. Trigger demo
    trigger_error = None
    try:
        conn = get_db_connection()
        conn.autocommit(False)
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT student_id, job_id FROM applications LIMIT 1")
                ex = cursor.fetchone()
                if ex:
                    cursor.execute("INSERT INTO applications (student_id,job_id) VALUES (%s,%s)",
                                   (ex['student_id'], ex['job_id']))
        except Exception as e:
            trigger_error = str(e)
        finally:
            conn.rollback()
            conn.close()
    except Exception as e:
        trigger_error = str(e)

    demos.append({
        'title': '9. Trigger — Preventing Duplicate Applications',
        'sql': "-- BEFORE INSERT trigger checks for existing row:\n-- CREATE TRIGGER trg_prevent_duplicate_application\n-- BEFORE INSERT ON applications FOR EACH ROW\n-- BEGIN\n--   IF EXISTS(SELECT 1 FROM applications\n--     WHERE student_id=NEW.student_id AND job_id=NEW.job_id)\n--   THEN SIGNAL SQLSTATE '45000'\n--     SET MESSAGE_TEXT='Duplicate application...';\n--   END IF;\n-- END\n\nINSERT INTO applications (student_id, job_id) VALUES (1, 1); -- Blocked!",
        'explanation': 'BEFORE INSERT triggers execute before data is written. This trigger checks for duplicates and raises a SIGNAL error with a descriptive message.',
        'results': None,
        'trigger_error': trigger_error or 'No data to demonstrate.',
        'is_trigger': True
    })

    # 10. Transaction demo
    demos.append({
        'title': '10. Transaction — Safe Offer Acceptance with Rollback',
        'sql': "START TRANSACTION;\n\n-- Step 1: Accept the offer\nUPDATE offers SET offer_status = 'Accepted' WHERE offer_id = @id;\n\n-- Step 2: Update application status\nUPDATE applications SET status = 'Selected' WHERE application_id = @app_id;\n\n-- Step 3: Decline other pending offers\nUPDATE offers SET offer_status = 'Declined'\nWHERE student_id = @sid AND offer_id <> @id AND offer_status = 'Pending';\n\n-- If ALL succeed: COMMIT;\n-- If ANY fails:   ROLLBACK;  -- undoes everything atomically",
        'explanation': 'Transactions ensure ACID properties — all operations succeed (COMMIT) or none do (ROLLBACK). The offer acceptance procedure atomically updates three tables.',
        'results': None,
        'is_transaction': True
    })

    return render_template('showcase/index.html', demos=demos)
