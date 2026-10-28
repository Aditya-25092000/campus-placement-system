-- ============================================================================
-- Campus Placement & Eligibility Management System
-- Stored Procedures (MySQL 8+)
-- ============================================================================
-- Business-logic procedures for placement reporting and eligibility checks.
-- ============================================================================

USE campus_placement;

-- ============================================================================
-- a. sp_department_placement_summary
-- ----------------------------------------------------------------------------
-- Returns a department-wise summary:
--   • Total students
--   • Students who applied to at least one job
--   • Students selected (application status = 'Selected')
--   • Students placed (accepted offer)
--   • Average CGPA of placed students
--   • Highest CTC offered to placed students
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_department_placement_summary;

DELIMITER $$

CREATE PROCEDURE sp_department_placement_summary()
BEGIN
    SELECT
        d.dept_name                                              AS department,
        COUNT(DISTINCT s.student_id)                             AS total_students,
        COUNT(DISTINCT CASE
            WHEN a.application_id IS NOT NULL THEN s.student_id
        END)                                                     AS applied_count,
        COUNT(DISTINCT CASE
            WHEN a.status = 'Selected' THEN s.student_id
        END)                                                     AS selected_count,
        COUNT(DISTINCT CASE
            WHEN o.offer_status = 'Accepted' THEN s.student_id
        END)                                                     AS placed_count,
        ROUND(AVG(CASE
            WHEN o.offer_status = 'Accepted' THEN s.cgpa
        END), 2)                                                 AS avg_cgpa_placed,
        COALESCE(MAX(CASE
            WHEN o.offer_status = 'Accepted' THEN o.ctc_lpa
        END), 0)                                                 AS highest_ctc_lpa
    FROM departments d
    LEFT JOIN students s       ON s.department_id  = d.department_id
    LEFT JOIN applications a   ON a.student_id     = s.student_id
    LEFT JOIN offers o         ON o.application_id = a.application_id
    GROUP BY d.department_id, d.dept_name
    ORDER BY d.dept_name;
END$$

DELIMITER ;


-- ============================================================================
-- b. sp_get_eligible_candidates
-- ----------------------------------------------------------------------------
-- For a given job_id, returns all students who meet EVERY eligibility
-- criterion:
--   1. CGPA >= job's min_cgpa
--   2. active_backlogs <= job's max_backlogs
--   3. graduation_year = job's eligible_grad_year (if specified)
--   4. Student's department is in job_allowed_departments
--   5. Student possesses ALL skills listed in job_required_skills
--   6. Student has NOT already applied
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_eligible_candidates;

DELIMITER $$

CREATE PROCEDURE sp_get_eligible_candidates(IN p_job_id INT)
BEGIN
    DECLARE v_min_cgpa        DECIMAL(4,2);
    DECLARE v_max_backlogs    INT;
    DECLARE v_grad_year       INT;
    DECLARE v_required_skills INT;

    -- Fetch job criteria
    SELECT min_cgpa, max_backlogs, eligible_grad_year
    INTO   v_min_cgpa, v_max_backlogs, v_grad_year
    FROM   job_postings
    WHERE  job_id = p_job_id;

    -- Count required skills for this job
    SELECT COUNT(*)
    INTO   v_required_skills
    FROM   job_required_skills
    WHERE  job_id = p_job_id;

    -- Return eligible students
    SELECT
        s.student_id,
        s.enrollment_no,
        s.full_name,
        s.email,
        s.phone,
        d.dept_name,
        s.graduation_year,
        s.cgpa,
        s.active_backlogs,
        GROUP_CONCAT(DISTINCT sk.skill_name ORDER BY sk.skill_name SEPARATOR ', ') AS student_skills
    FROM students s
    INNER JOIN departments d ON d.department_id = s.department_id
    -- 4. Department must be in allowed departments for this job
    INNER JOIN job_allowed_departments jad
        ON jad.department_id = s.department_id
        AND jad.job_id = p_job_id
    -- Join student skills to check required skills
    LEFT JOIN student_skills ss ON ss.student_id = s.student_id
    LEFT JOIN skills sk         ON sk.skill_id   = ss.skill_id
    WHERE
        -- 1. CGPA check
        s.cgpa >= v_min_cgpa
        -- 2. Backlogs check
        AND s.active_backlogs <= v_max_backlogs
        -- 3. Graduation year check (NULL means all years eligible)
        AND (v_grad_year IS NULL OR s.graduation_year = v_grad_year)
        -- 6. Student has not already applied
        AND s.student_id NOT IN (
            SELECT a.student_id
            FROM applications a
            WHERE a.job_id = p_job_id
        )
    GROUP BY
        s.student_id, s.enrollment_no, s.full_name,
        s.email, s.phone, d.dept_name,
        s.graduation_year, s.cgpa, s.active_backlogs
    HAVING
        -- 5. Student has ALL required skills (if any)
        v_required_skills = 0
        OR SUM(CASE
            WHEN ss.skill_id IN (
                SELECT jrs.skill_id FROM job_required_skills jrs WHERE jrs.job_id = p_job_id
            ) THEN 1 ELSE 0
        END) >= v_required_skills
    ORDER BY s.cgpa DESC, s.full_name;
END$$

DELIMITER ;


-- ============================================================================
-- c. sp_process_offer_acceptance
-- ----------------------------------------------------------------------------
-- Accepts a specific offer and declines all other pending offers for the
-- same student, within a transaction. Also updates the related application
-- status to 'Selected'.
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_process_offer_acceptance;

DELIMITER $$

CREATE PROCEDURE sp_process_offer_acceptance(IN p_offer_id INT)
BEGIN
    DECLARE v_student_id      INT;
    DECLARE v_application_id  INT;
    DECLARE v_current_status  VARCHAR(20);

    -- Error handler — rollback on any SQL exception
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Validate the offer exists and is still pending
    SELECT student_id, application_id, offer_status
    INTO   v_student_id, v_application_id, v_current_status
    FROM   offers
    WHERE  offer_id = p_offer_id;

    IF v_student_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Offer not found.';
    END IF;

    IF v_current_status <> 'Pending' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Only pending offers can be accepted.';
    END IF;

    START TRANSACTION;

    -- 1. Accept the specified offer
    UPDATE offers
    SET    offer_status = 'Accepted'
    WHERE  offer_id = p_offer_id;

    -- 2. Update the related application to 'Selected'
    UPDATE applications
    SET    status = 'Selected'
    WHERE  application_id = v_application_id;

    -- 3. Decline all other pending offers for the same student
    UPDATE offers
    SET    offer_status = 'Declined'
    WHERE  student_id   = v_student_id
      AND  offer_id    <> p_offer_id
      AND  offer_status = 'Pending';

    COMMIT;
END$$

DELIMITER ;

-- ============================================================================
-- Stored procedures creation complete.
-- ============================================================================
