-- ============================================================================
-- Campus Placement & Eligibility Management System
-- MySQL Triggers
-- ============================================================================
-- Business-rule enforcement triggers that guard data integrity beyond what
-- simple constraints can achieve.
-- ============================================================================

USE campus_placement;

-- ============================================================================
-- a. trg_prevent_duplicate_application
-- ----------------------------------------------------------------------------
-- BEFORE INSERT on `applications`
-- Prevents a student from applying to the same job more than once.
-- (The UNIQUE KEY also enforces this, but the trigger provides a clear
-- user-facing error message.)
-- ============================================================================
DROP TRIGGER IF EXISTS trg_prevent_duplicate_application;

DELIMITER $$

CREATE TRIGGER trg_prevent_duplicate_application
BEFORE INSERT ON applications
FOR EACH ROW
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*)
    INTO   v_count
    FROM   applications
    WHERE  student_id = NEW.student_id
      AND  job_id     = NEW.job_id;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Duplicate application: This student has already applied for this job.';
    END IF;
END$$

DELIMITER ;


-- ============================================================================
-- b. trg_validate_application_eligibility
-- ----------------------------------------------------------------------------
-- BEFORE INSERT on `applications`
-- Ensures the job is still Active and the application deadline has not passed.
-- ============================================================================
DROP TRIGGER IF EXISTS trg_validate_application_eligibility;

DELIMITER $$

CREATE TRIGGER trg_validate_application_eligibility
BEFORE INSERT ON applications
FOR EACH ROW
BEGIN
    DECLARE v_job_status  VARCHAR(10);
    DECLARE v_deadline    DATE;

    SELECT status, application_deadline
    INTO   v_job_status, v_deadline
    FROM   job_postings
    WHERE  job_id = NEW.job_id;

    IF v_job_status <> 'Active' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot apply: This job posting is not currently active.';
    END IF;

    IF v_deadline < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot apply: The application deadline for this job has passed.';
    END IF;
END$$

DELIMITER ;


-- ============================================================================
-- c. trg_enforce_single_accepted_offer_insert
-- ----------------------------------------------------------------------------
-- BEFORE INSERT on `offers`
-- If the new offer is being inserted with status 'Accepted', verify the
-- student does not already have another accepted offer.
-- ============================================================================
DROP TRIGGER IF EXISTS trg_enforce_single_accepted_offer_insert;

DELIMITER $$

CREATE TRIGGER trg_enforce_single_accepted_offer_insert
BEFORE INSERT ON offers
FOR EACH ROW
BEGIN
    DECLARE v_accepted_count INT;

    IF NEW.offer_status = 'Accepted' THEN
        SELECT COUNT(*)
        INTO   v_accepted_count
        FROM   offers
        WHERE  student_id   = NEW.student_id
          AND  offer_status = 'Accepted';

        IF v_accepted_count > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Cannot accept offer: This student already has an accepted offer.';
        END IF;
    END IF;
END$$

DELIMITER ;


-- ============================================================================
-- c. trg_enforce_single_accepted_offer_update
-- ----------------------------------------------------------------------------
-- BEFORE UPDATE on `offers`
-- If offer_status is being changed to 'Accepted', verify the student does
-- not already have another accepted offer (excluding the current row).
-- ============================================================================
DROP TRIGGER IF EXISTS trg_enforce_single_accepted_offer_update;

DELIMITER $$

CREATE TRIGGER trg_enforce_single_accepted_offer_update
BEFORE UPDATE ON offers
FOR EACH ROW
BEGIN
    DECLARE v_accepted_count INT;

    IF NEW.offer_status = 'Accepted' AND OLD.offer_status <> 'Accepted' THEN
        SELECT COUNT(*)
        INTO   v_accepted_count
        FROM   offers
        WHERE  student_id   = NEW.student_id
          AND  offer_status = 'Accepted'
          AND  offer_id    <> OLD.offer_id;

        IF v_accepted_count > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Cannot accept offer: This student already has an accepted offer.';
        END IF;
    END IF;
END$$

DELIMITER ;


-- ============================================================================
-- d. trg_update_application_on_offer
-- ----------------------------------------------------------------------------
-- AFTER UPDATE on `offers`
-- When an offer is accepted, automatically set the related application
-- status to 'Selected'.
-- ============================================================================
DROP TRIGGER IF EXISTS trg_update_application_on_offer;

DELIMITER $$

CREATE TRIGGER trg_update_application_on_offer
AFTER UPDATE ON offers
FOR EACH ROW
BEGIN
    IF NEW.offer_status = 'Accepted' AND OLD.offer_status <> 'Accepted' THEN
        UPDATE applications
        SET    status = 'Selected'
        WHERE  application_id = NEW.application_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- Triggers creation complete.
-- ============================================================================
