"""Eligibility checking service for job postings.

Evaluates student profiles against job posting criteria.
Produces detailed eligibility results with reasons.
"""
from db import execute_query
from datetime import date


def check_student_eligibility(student_id, job_id):
    """Check if a single student is eligible for a specific job.

    Returns dict with keys: eligible (bool), reasons (list), details (dict).
    """
    # Fetch student details
    student = execute_query(
        """SELECT s.student_id, s.enrollment_no, s.full_name, s.cgpa,
                  s.active_backlogs, s.graduation_year, s.department_id,
                  d.dept_name, d.dept_code
           FROM students s
           INNER JOIN departments d ON d.department_id = s.department_id
           WHERE s.student_id = %s""",
        (student_id,), fetchone=True
    )
    if not student:
        return {'eligible': False, 'reasons': ['Student not found'], 'details': {}}

    # Fetch job details
    job = execute_query(
        """SELECT jp.*, c.company_name
           FROM job_postings jp
           INNER JOIN companies c ON c.company_id = jp.company_id
           WHERE jp.job_id = %s""",
        (job_id,), fetchone=True
    )
    if not job:
        return {'eligible': False, 'reasons': ['Job posting not found'], 'details': {}}

    reasons = []

    # 1. Job status check
    if job['status'] != 'Active':
        reasons.append(f"Job posting is {job['status']}")

    # 2. Deadline check
    if job['application_deadline'] and job['application_deadline'] < date.today():
        reasons.append('Application deadline has passed')

    # 3. CGPA check
    if job['min_cgpa'] and student['cgpa'] < job['min_cgpa']:
        reasons.append(f"CGPA {student['cgpa']} is below minimum required {job['min_cgpa']}")

    # 4. Backlogs check
    if job['max_backlogs'] is not None and student['active_backlogs'] > job['max_backlogs']:
        reasons.append(
            f"Active backlogs ({student['active_backlogs']}) exceed maximum allowed ({job['max_backlogs']})")

    # 5. Graduation year check
    if job['eligible_grad_year'] is not None:
        if student['graduation_year'] != job['eligible_grad_year']:
            reasons.append(
                f"Graduation year {student['graduation_year']} does not match required {job['eligible_grad_year']}")

    # 6. Department check
    allowed_depts = execute_query(
        "SELECT department_id FROM job_allowed_departments WHERE job_id = %s",
        (job_id,)
    )
    if allowed_depts:
        allowed_dept_ids = [d['department_id'] for d in allowed_depts]
        if student['department_id'] not in allowed_dept_ids:
            allowed_names = execute_query(
                "SELECT dept_name FROM departments WHERE department_id IN ({})".format(
                    ','.join(['%s'] * len(allowed_dept_ids))
                ), tuple(allowed_dept_ids)
            )
            dept_names = ', '.join([d['dept_name'] for d in allowed_names])
            reasons.append(f"Department {student['dept_name']} not eligible (allowed: {dept_names})")

    # 7. Required skills check
    required_skills = execute_query(
        """SELECT sk.skill_id, sk.skill_name
           FROM job_required_skills jrs
           INNER JOIN skills sk ON sk.skill_id = jrs.skill_id
           WHERE jrs.job_id = %s""",
        (job_id,)
    )
    if required_skills:
        student_skills = execute_query(
            "SELECT skill_id FROM student_skills WHERE student_id = %s",
            (student_id,)
        )
        student_skill_ids = {s['skill_id'] for s in student_skills}
        missing = [s['skill_name'] for s in required_skills if s['skill_id'] not in student_skill_ids]
        if missing:
            reasons.append(f"Missing required skills: {', '.join(missing)}")

    return {
        'eligible': len(reasons) == 0,
        'reasons': reasons if reasons else ['All criteria met'],
        'details': {'student': student, 'job': job}
    }


def get_eligible_students_for_job(job_id):
    """Get all students classified as eligible or ineligible for a job.

    Returns (eligible_list, ineligible_list, job_dict).
    """
    job = execute_query(
        """SELECT jp.*, c.company_name
           FROM job_postings jp
           INNER JOIN companies c ON c.company_id = jp.company_id
           WHERE jp.job_id = %s""",
        (job_id,), fetchone=True
    )
    if not job:
        return [], [], None

    # Get all students with their skills
    all_students = execute_query("""
        SELECT s.student_id, s.enrollment_no, s.full_name, s.email, s.phone,
               s.cgpa, s.active_backlogs, s.graduation_year,
               s.department_id, d.dept_name, d.dept_code,
               GROUP_CONCAT(DISTINCT sk.skill_name ORDER BY sk.skill_name SEPARATOR ', ') AS skills
        FROM students s
        INNER JOIN departments d ON d.department_id = s.department_id
        LEFT JOIN student_skills ss ON ss.student_id = s.student_id
        LEFT JOIN skills sk ON sk.skill_id = ss.skill_id
        GROUP BY s.student_id, s.enrollment_no, s.full_name, s.email, s.phone,
                 s.cgpa, s.active_backlogs, s.graduation_year,
                 s.department_id, d.dept_name, d.dept_code
        ORDER BY s.cgpa DESC, s.full_name
    """)

    allowed_depts = execute_query(
        "SELECT department_id FROM job_allowed_departments WHERE job_id = %s", (job_id,))
    allowed_dept_ids = {d['department_id'] for d in allowed_depts} if allowed_depts else set()

    required_skills = execute_query(
        """SELECT sk.skill_id, sk.skill_name
           FROM job_required_skills jrs
           INNER JOIN skills sk ON sk.skill_id = jrs.skill_id
           WHERE jrs.job_id = %s""", (job_id,))
    required_skill_names = {s['skill_name'] for s in required_skills} if required_skills else set()

    existing_apps = execute_query(
        "SELECT student_id, status FROM applications WHERE job_id = %s", (job_id,))
    app_map = {a['student_id']: a['status'] for a in existing_apps} if existing_apps else {}

    eligible, ineligible = [], []

    for student in all_students:
        reasons = []
        if job['min_cgpa'] and student['cgpa'] < job['min_cgpa']:
            reasons.append(f"CGPA below minimum ({student['cgpa']} < {job['min_cgpa']})")
        if job['max_backlogs'] is not None and student['active_backlogs'] > job['max_backlogs']:
            reasons.append(f"Too many backlogs ({student['active_backlogs']} > {job['max_backlogs']})")
        if job['eligible_grad_year'] is not None and student['graduation_year'] != job['eligible_grad_year']:
            reasons.append(f"Graduation year mismatch ({student['graduation_year']} ≠ {job['eligible_grad_year']})")
        if allowed_dept_ids and student['department_id'] not in allowed_dept_ids:
            reasons.append(f"Department not eligible ({student['dept_name']})")
        if required_skill_names:
            student_skill_set = set(student['skills'].split(', ')) if student['skills'] else set()
            missing = required_skill_names - student_skill_set
            if missing:
                reasons.append(f"Missing skills: {', '.join(sorted(missing))}")

        student_data = dict(student)
        student_data['application_status'] = app_map.get(student['student_id'])

        if not reasons:
            student_data['eligible'] = True
            student_data['reasons'] = ['All criteria met']
            eligible.append(student_data)
        else:
            student_data['eligible'] = False
            student_data['reasons'] = reasons
            ineligible.append(student_data)

    return eligible, ineligible, job


def get_eligible_jobs_for_student(student_id):
    """Get all active jobs a student is eligible for."""
    jobs = execute_query(
        """SELECT jp.*, c.company_name
           FROM job_postings jp
           INNER JOIN companies c ON c.company_id = jp.company_id
           WHERE jp.status = 'Active' AND jp.application_deadline >= CURDATE()
           ORDER BY jp.application_deadline""")

    results = []
    for job in jobs:
        result = check_student_eligibility(student_id, job['job_id'])
        job_data = dict(job)
        job_data['eligible'] = result['eligible']
        job_data['reasons'] = result['reasons']
        results.append(job_data)
    return results
