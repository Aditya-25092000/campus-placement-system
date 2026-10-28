-- ============================================================================
-- Campus Placement & Eligibility Management System
-- MySQL Views
-- ============================================================================
-- These views provide convenient, pre-joined read-only perspectives of the
-- data for dashboards, reports, and application queries.
-- ============================================================================

USE campus_placement;

-- ============================================================================
-- a. vw_placement_summary
-- ----------------------------------------------------------------------------
-- Department-wise placement overview: total students, placed count,
-- placement percentage, and average CTC of accepted offers.
-- ============================================================================
CREATE OR REPLACE VIEW vw_placement_summary AS
SELECT
    d.department_id,
    d.dept_name,
    d.dept_code,
    COUNT(DISTINCT s.student_id)                          AS total_students,
    COUNT(DISTINCT CASE
        WHEN o.offer_status = 'Accepted' THEN s.student_id
    END)                                                  AS students_placed,
    ROUND(
        COUNT(DISTINCT CASE
            WHEN o.offer_status = 'Accepted' THEN s.student_id
        END) * 100.0
        / NULLIF(COUNT(DISTINCT s.student_id), 0), 2
    )                                                     AS placement_percentage,
    ROUND(AVG(
        CASE WHEN o.offer_status = 'Accepted' THEN o.ctc_lpa END
    ), 2)                                                 AS avg_ctc_lpa
FROM departments d
LEFT JOIN students s       ON s.department_id = d.department_id
LEFT JOIN applications a   ON a.student_id    = s.student_id
LEFT JOIN offers o         ON o.application_id = a.application_id
GROUP BY d.department_id, d.dept_name, d.dept_code;

-- ============================================================================
-- b. vw_student_details
-- ----------------------------------------------------------------------------
-- Flattened student view with department information.
-- ============================================================================
CREATE OR REPLACE VIEW vw_student_details AS
SELECT
    s.student_id,
    s.enrollment_no,
    s.full_name,
    s.email,
    s.phone,
    d.dept_name,
    d.dept_code,
    s.graduation_year,
    s.cgpa,
    s.active_backlogs,
    s.registration_date
FROM students s
INNER JOIN departments d ON d.department_id = s.department_id;

-- ============================================================================
-- c. vw_application_details
-- ----------------------------------------------------------------------------
-- Full application view joining students, departments, jobs, and companies.
-- ============================================================================
CREATE OR REPLACE VIEW vw_application_details AS
SELECT
    a.application_id,
    s.enrollment_no,
    s.full_name        AS student_name,
    d.dept_name,
    jp.job_title,
    c.company_name,
    a.status           AS application_status,
    a.applied_date
FROM applications a
INNER JOIN students s       ON s.student_id    = a.student_id
INNER JOIN departments d    ON d.department_id = s.department_id
INNER JOIN job_postings jp  ON jp.job_id       = a.job_id
INNER JOIN companies c      ON c.company_id    = jp.company_id;

-- ============================================================================
-- d. vw_active_job_postings
-- ----------------------------------------------------------------------------
-- Active jobs enriched with company name, eligible department count,
-- and required skill count.
-- ============================================================================
CREATE OR REPLACE VIEW vw_active_job_postings AS
SELECT
    jp.job_id,
    jp.job_title,
    c.company_name,
    jp.job_type,
    jp.job_location,
    jp.min_cgpa,
    jp.max_backlogs,
    jp.eligible_grad_year,
    jp.application_open_date,
    jp.application_deadline,
    jp.status,
    COUNT(DISTINCT jad.department_id) AS eligible_dept_count,
    COUNT(DISTINCT jrs.skill_id)      AS required_skill_count
FROM job_postings jp
INNER JOIN companies c                ON c.company_id   = jp.company_id
LEFT JOIN job_allowed_departments jad ON jad.job_id      = jp.job_id
LEFT JOIN job_required_skills jrs    ON jrs.job_id       = jp.job_id
WHERE jp.status = 'Active'
GROUP BY
    jp.job_id, jp.job_title, c.company_name, jp.job_type,
    jp.job_location, jp.min_cgpa, jp.max_backlogs,
    jp.eligible_grad_year, jp.application_open_date,
    jp.application_deadline, jp.status;

-- ============================================================================
-- Views creation complete.
-- ============================================================================
