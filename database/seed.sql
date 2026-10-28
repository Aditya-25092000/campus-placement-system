-- ============================================================================
-- Campus Placement & Eligibility Management System
-- Seed / Sample Data (MySQL 8+)
-- ============================================================================
-- Realistic sample data for development and testing.
-- Uses INSERT IGNORE to allow safe re-runs without duplicate errors.
-- ============================================================================

USE campus_placement;

-- ============================================================================
-- DEPARTMENTS (4)
-- ============================================================================
INSERT IGNORE INTO departments (department_id, dept_name, dept_code) VALUES
    (1, 'Computer Science',             'CS'),
    (2, 'Information Technology',        'IT'),
    (3, 'Electronics & Communication',   'ECE'),
    (4, 'Mechanical Engineering',        'ME');

-- ============================================================================
-- SKILLS (8)
-- ============================================================================
INSERT IGNORE INTO skills (skill_id, skill_name) VALUES
    (1, 'Python'),
    (2, 'Java'),
    (3, 'JavaScript'),
    (4, 'SQL'),
    (5, 'C++'),
    (6, 'Machine Learning'),
    (7, 'Data Structures'),
    (8, 'Web Development');

-- ============================================================================
-- ADMIN USER
-- ----------------------------------------------------------------------------
-- NOTE: The password hash below is a placeholder. The Flask application will
-- seed the real admin user programmatically with a proper Werkzeug hash.
-- ============================================================================
INSERT IGNORE INTO admin_users (admin_id, username, password_hash, full_name, email) VALUES
    (1, 'admin', 'SEEDED_BY_APP', 'Administrator', 'admin@campus.edu');

-- ============================================================================
-- STUDENTS (25)
-- Spread across CS (1), IT (2), ECE (3), ME (4)
-- CGPA range 5.0 – 9.8 | Graduation years 2026 & 2027
-- Most have 0 backlogs; a few have 1–3
-- ============================================================================
INSERT IGNORE INTO students
    (student_id, enrollment_no, full_name, email, phone, department_id, graduation_year, cgpa, active_backlogs, registration_date)
VALUES
    -- Computer Science (dept 1)
    ( 1, 'CS2026001', 'Aarav Sharma',      'aarav.sharma@campus.edu',     '9876543210', 1, 2026, 9.20, 0, '2025-08-01'),
    ( 2, 'CS2026002', 'Diya Patel',        'diya.patel@campus.edu',       '9876543211', 1, 2026, 8.50, 0, '2025-08-01'),
    ( 3, 'CS2026003', 'Vivaan Kumar',      'vivaan.kumar@campus.edu',     '9876543212', 1, 2026, 7.30, 0, '2025-08-02'),
    ( 4, 'CS2026004', 'Ananya Singh',      'ananya.singh@campus.edu',     '9876543213', 1, 2026, 6.10, 1, '2025-08-03'),
    ( 5, 'CS2027001', 'Rohan Gupta',       'rohan.gupta@campus.edu',      '9876543214', 1, 2027, 8.80, 0, '2025-08-05'),
    ( 6, 'CS2027002', 'Meera Reddy',       'meera.reddy@campus.edu',      '9876543215', 1, 2027, 7.60, 0, '2025-08-05'),
    ( 7, 'CS2026005', 'Kabir Joshi',       'kabir.joshi@campus.edu',      '9876543216', 1, 2026, 5.80, 2, '2025-08-06'),

    -- Information Technology (dept 2)
    ( 8, 'IT2026001', 'Priya Nair',        'priya.nair@campus.edu',       '9876543217', 2, 2026, 8.90, 0, '2025-08-01'),
    ( 9, 'IT2026002', 'Arjun Menon',       'arjun.menon@campus.edu',      '9876543218', 2, 2026, 7.40, 0, '2025-08-02'),
    (10, 'IT2026003', 'Sneha Iyer',        'sneha.iyer@campus.edu',       '9876543219', 2, 2026, 6.70, 1, '2025-08-03'),
    (11, 'IT2027001', 'Aditya Rao',        'aditya.rao@campus.edu',       '9876543220', 2, 2027, 9.10, 0, '2025-08-04'),
    (12, 'IT2027002', 'Ishita Verma',      'ishita.verma@campus.edu',     '9876543221', 2, 2027, 7.80, 0, '2025-08-05'),
    (13, 'IT2026004', 'Rahul Deshmukh',    'rahul.deshmukh@campus.edu',   '9876543222', 2, 2026, 5.50, 3, '2025-08-06'),

    -- Electronics & Communication (dept 3)
    (14, 'ECE2026001', 'Kavya Pillai',     'kavya.pillai@campus.edu',     '9876543223', 3, 2026, 8.30, 0, '2025-08-01'),
    (15, 'ECE2026002', 'Nikhil Saxena',    'nikhil.saxena@campus.edu',    '9876543224', 3, 2026, 7.10, 0, '2025-08-02'),
    (16, 'ECE2026003', 'Pooja Chatterjee', 'pooja.chatterjee@campus.edu', '9876543225', 3, 2026, 6.40, 1, '2025-08-03'),
    (17, 'ECE2027001', 'Siddharth Mishra', 'siddharth.mishra@campus.edu', '9876543226', 3, 2027, 9.50, 0, '2025-08-04'),
    (18, 'ECE2027002', 'Riya Banerjee',    'riya.banerjee@campus.edu',    '9876543227', 3, 2027, 7.90, 0, '2025-08-05'),
    (19, 'ECE2026004', 'Deepak Thakur',    'deepak.thakur@campus.edu',    '9876543228', 3, 2026, 5.20, 2, '2025-08-06'),

    -- Mechanical Engineering (dept 4)
    (20, 'ME2026001',  'Amit Tiwari',      'amit.tiwari@campus.edu',      '9876543229', 4, 2026, 8.60, 0, '2025-08-01'),
    (21, 'ME2026002',  'Shruti Kulkarni',  'shruti.kulkarni@campus.edu',  '9876543230', 4, 2026, 7.50, 0, '2025-08-02'),
    (22, 'ME2026003',  'Vikram Chauhan',   'vikram.chauhan@campus.edu',   '9876543231', 4, 2026, 6.80, 0, '2025-08-03'),
    (23, 'ME2027001',  'Neha Agarwal',     'neha.agarwal@campus.edu',     '9876543232', 4, 2027, 9.00, 0, '2025-08-04'),
    (24, 'ME2027002',  'Karan Malhotra',   'karan.malhotra@campus.edu',   '9876543233', 4, 2027, 5.00, 1, '2025-08-05'),
    (25, 'ME2026004',  'Tanvi Jain',       'tanvi.jain@campus.edu',       '9876543234', 4, 2026, 9.80, 0, '2025-08-06');

-- ============================================================================
-- STUDENT SKILLS (2–4 skills per student)
-- ============================================================================
INSERT IGNORE INTO student_skills (student_id, skill_id) VALUES
    -- Aarav (CS) : Python, Java, Data Structures, SQL
    (1, 1), (1, 2), (1, 7), (1, 4),
    -- Diya (CS) : Python, Data Structures, Machine Learning
    (2, 1), (2, 7), (2, 6),
    -- Vivaan (CS) : Java, SQL, Web Development
    (3, 2), (3, 4), (3, 8),
    -- Ananya (CS) : JavaScript, Web Development
    (4, 3), (4, 8),
    -- Rohan (CS) : Python, Java, Data Structures
    (5, 1), (5, 2), (5, 7),
    -- Meera (CS) : Python, SQL, Machine Learning
    (6, 1), (6, 4), (6, 6),
    -- Kabir (CS) : C++, Data Structures
    (7, 5), (7, 7),
    -- Priya (IT) : Python, Java, SQL, Web Development
    (8, 1), (8, 2), (8, 4), (8, 8),
    -- Arjun (IT) : JavaScript, Web Development, SQL
    (9, 3), (9, 8), (9, 4),
    -- Sneha (IT) : Java, SQL
    (10, 2), (10, 4),
    -- Aditya (IT) : Python, Java, Data Structures, SQL
    (11, 1), (11, 2), (11, 7), (11, 4),
    -- Ishita (IT) : JavaScript, Web Development, Python
    (12, 3), (12, 8), (12, 1),
    -- Rahul (IT) : Java, C++
    (13, 2), (13, 5),
    -- Kavya (ECE) : Python, SQL, Machine Learning
    (14, 1), (14, 4), (14, 6),
    -- Nikhil (ECE) : C++, Data Structures, Java
    (15, 5), (15, 7), (15, 2),
    -- Pooja (ECE) : Python, SQL
    (16, 1), (16, 4),
    -- Siddharth (ECE) : Python, C++, Data Structures, Machine Learning
    (17, 1), (17, 5), (17, 7), (17, 6),
    -- Riya (ECE) : Java, SQL, Web Development
    (18, 2), (18, 4), (18, 8),
    -- Deepak (ECE) : C++, Data Structures
    (19, 5), (19, 7),
    -- Amit (ME) : C++, Data Structures, Python
    (20, 5), (20, 7), (20, 1),
    -- Shruti (ME) : C++, Java
    (21, 5), (21, 2),
    -- Vikram (ME) : C++, SQL
    (22, 5), (22, 4),
    -- Neha (ME) : Python, C++, Machine Learning
    (23, 1), (23, 5), (23, 6),
    -- Karan (ME) : C++
    (24, 5),
    -- Tanvi (ME) : C++, Data Structures, Python, Java
    (25, 5), (25, 7), (25, 1), (25, 2);

-- ============================================================================
-- COMPANIES (6)
-- ============================================================================
INSERT IGNORE INTO companies
    (company_id, company_name, industry, website, hr_contact_name, hr_email, contact_number, description)
VALUES
    (1, 'TCS',         'IT Services',            'https://www.tcs.com',       'Neelam Kapoor',   'hr@tcs.com',       '1800111100', 'Tata Consultancy Services — Global IT services and consulting.'),
    (2, 'Infosys',     'IT Services',            'https://www.infosys.com',   'Raghav Srinivasan','hr@infosys.com',  '1800222200', 'Infosys Limited — Digital services and consulting.'),
    (3, 'Google',      'Technology',             'https://careers.google.com','Sarah Chen',       'hr@google.com',    '1800333300', 'Google LLC — Search, cloud, and AI technology company.'),
    (4, 'Amazon',      'E-commerce/Technology',  'https://www.amazon.jobs',   'Prateek Jha',     'hr@amazon.com',    '1800444400', 'Amazon — E-commerce and cloud computing leader.'),
    (5, 'Wipro',       'IT Services',            'https://www.wipro.com',     'Sunita Rao',      'hr@wipro.com',     '1800555500', 'Wipro Limited — IT, consulting, and business process services.'),
    (6, 'Tata Motors', 'Automotive',             'https://www.tatamotors.com','Manish Dubey',    'hr@tatamotors.com','1800666600', 'Tata Motors — Automobile manufacturer and EV pioneer.');

-- ============================================================================
-- JOB POSTINGS (7)
-- ============================================================================
INSERT IGNORE INTO job_postings
    (job_id, company_id, job_title, job_description, job_location, job_type,
     min_cgpa, max_backlogs, eligible_grad_year,
     application_open_date, application_deadline, status)
VALUES
    -- 1. TCS - Software Developer
    (1, 1, 'Software Developer',
     'Join TCS as a Software Developer working on enterprise Java/Spring applications.',
     'Mumbai', 'Full-time',
     6.00, 0, 2026,
     '2026-08-15', '2026-11-30', 'Active'),

    -- 2. Infosys - Systems Engineer
    (2, 2, 'Systems Engineer',
     'Infosys Systems Engineer role across multiple technology stacks.',
     'Bengaluru', 'Full-time',
     6.50, 1, 2026,
     '2026-09-01', '2026-12-15', 'Active'),

    -- 3. Google - SDE Intern
    (3, 3, 'SDE Intern',
     'Summer internship at Google focused on algorithms and scalable systems.',
     'Hyderabad', 'Internship',
     8.00, 0, 2027,
     '2026-09-15', '2026-12-31', 'Active'),

    -- 4. Amazon - Data Analyst
    (4, 4, 'Data Analyst',
     'Analyze large datasets using Python and SQL to drive business decisions at Amazon.',
     'Bengaluru', 'Full-time',
     7.00, 0, 2026,
     '2026-08-20', '2026-11-15', 'Active'),

    -- 5. Wipro - Full Stack Developer
    (5, 5, 'Full Stack Developer',
     'Build modern web applications with React and Node.js at Wipro.',
     'Pune', 'Full-time',
     6.00, 1, 2026,
     '2026-09-10', '2026-12-20', 'Active'),

    -- 6. Tata Motors - Design Engineer
    (6, 6, 'Design Engineer',
     'Work on automotive component design and simulation at Tata Motors.',
     'Pune', 'Full-time',
     6.50, 0, 2026,
     '2026-10-01', '2027-01-15', 'Active'),

    -- 7. Google - Cloud Engineer (CLOSED)
    (7, 3, 'Cloud Engineer',
     'Google Cloud Platform infrastructure engineering role.',
     'Bengaluru', 'Full-time',
     7.50, 0, 2026,
     '2026-08-01', '2026-09-30', 'Closed');

-- ============================================================================
-- JOB ALLOWED DEPARTMENTS
-- ============================================================================
INSERT IGNORE INTO job_allowed_departments (job_id, department_id) VALUES
    -- Job 1: TCS Software Developer — CS, IT
    (1, 1), (1, 2),
    -- Job 2: Infosys Systems Engineer — All departments
    (2, 1), (2, 2), (2, 3), (2, 4),
    -- Job 3: Google SDE Intern — CS only
    (3, 1),
    -- Job 4: Amazon Data Analyst — CS, IT, ECE
    (4, 1), (4, 2), (4, 3),
    -- Job 5: Wipro Full Stack Dev — CS, IT
    (5, 1), (5, 2),
    -- Job 6: Tata Motors Design Engineer — ME, ECE
    (6, 3), (6, 4),
    -- Job 7: Google Cloud Engineer — CS, IT
    (7, 1), (7, 2);

-- ============================================================================
-- JOB REQUIRED SKILLS
-- ============================================================================
INSERT IGNORE INTO job_required_skills (job_id, skill_id) VALUES
    -- Job 1: TCS Software Developer — Java, SQL
    (1, 2), (1, 4),
    -- Job 2: Infosys Systems Engineer — (no specific skill requirement)
    -- Job 3: Google SDE Intern — Python, Data Structures
    (3, 1), (3, 7),
    -- Job 4: Amazon Data Analyst — Python, SQL, Machine Learning
    (4, 1), (4, 4), (4, 6),
    -- Job 5: Wipro Full Stack Dev — JavaScript, Web Development
    (5, 3), (5, 8),
    -- Job 6: Tata Motors Design Engineer — C++
    (6, 5),
    -- Job 7: Google Cloud Engineer — Python, SQL
    (7, 1), (7, 4);

-- ============================================================================
-- APPLICATIONS (~20)
-- Mix of statuses: Applied, Shortlisted, Interview, Selected, Rejected, Withdrawn
-- ============================================================================
-- NOTE: Triggers trg_prevent_duplicate_application and
-- trg_validate_application_eligibility will fire. The data below is designed
-- to satisfy those constraints (Active jobs, future deadlines, no duplicates).
-- For seed data we insert with explicit applied_date.
-- ============================================================================
INSERT IGNORE INTO applications
    (application_id, student_id, job_id, status, applied_date)
VALUES
    -- TCS Software Developer (job 1) — CS/IT students
    ( 1,  1, 1, 'Selected',    '2026-09-01 10:00:00'),   -- Aarav (CS, 9.2)
    ( 2,  3, 1, 'Interview',   '2026-09-02 11:30:00'),   -- Vivaan (CS, 7.3)
    ( 3,  8, 1, 'Selected',    '2026-09-03 09:15:00'),   -- Priya (IT, 8.9)
    ( 4,  9, 1, 'Rejected',    '2026-09-04 14:00:00'),   -- Arjun (IT, 7.4)

    -- Infosys Systems Engineer (job 2) — All depts
    ( 5,  2, 2, 'Interview',   '2026-09-15 10:00:00'),   -- Diya (CS, 8.5)
    ( 6, 14, 2, 'Shortlisted', '2026-09-16 11:00:00'),   -- Kavya (ECE, 8.3)
    ( 7, 20, 2, 'Applied',     '2026-09-17 12:00:00'),   -- Amit (ME, 8.6)
    ( 8, 10, 2, 'Rejected',    '2026-09-18 13:00:00'),   -- Sneha (IT, 6.7, 1 backlog)

    -- Google SDE Intern (job 3) — CS, 2027 grad
    ( 9,  5, 3, 'Interview',   '2026-10-01 10:00:00'),   -- Rohan (CS, 8.8)
    (10,  6, 3, 'Applied',     '2026-10-02 11:00:00'),   -- Meera (CS, 7.6 — below 8.0 but applied)

    -- Amazon Data Analyst (job 4) — CS/IT/ECE
    (11,  1, 4, 'Interview',   '2026-09-05 10:00:00'),   -- Aarav (CS, 9.2)
    (12,  8, 4, 'Shortlisted', '2026-09-06 11:00:00'),   -- Priya (IT, 8.9)
    (13, 14, 4, 'Selected',    '2026-09-07 12:00:00'),   -- Kavya (ECE, 8.3)

    -- Wipro Full Stack Dev (job 5) — CS/IT
    (14,  4, 5, 'Applied',     '2026-10-05 10:00:00'),   -- Ananya (CS, 6.1, 1 backlog)
    (15,  9, 5, 'Interview',   '2026-10-06 11:00:00'),   -- Arjun (IT, 7.4)
    (16, 12, 5, 'Applied',     '2026-10-07 12:00:00'),   -- Ishita (IT, 7.8)

    -- Tata Motors Design Engineer (job 6) — ME/ECE
    (17, 20, 6, 'Shortlisted', '2026-10-10 10:00:00'),   -- Amit (ME, 8.6)
    (18, 25, 6, 'Interview',   '2026-10-11 11:00:00'),   -- Tanvi (ME, 9.8)
    (19, 15, 6, 'Applied',     '2026-10-12 12:00:00'),   -- Nikhil (ECE, 7.1)

    -- Extra application
    (20,  2, 1, 'Shortlisted', '2026-09-20 10:00:00');   -- Diya (CS) also applied to TCS

-- ============================================================================
-- INTERVIEW ROUNDS (~15)
-- For applications in Interview / Selected status
-- ============================================================================
INSERT IGNORE INTO interview_rounds
    (interview_id, application_id, round_name, scheduled_date, interview_mode,
     location_details, status, result, feedback)
VALUES
    -- App 1: Aarav → TCS (Selected) — completed all rounds
    ( 1,  1, 'Aptitude',   '2026-09-10 09:00:00', 'Online',    'TCS iON Portal',       'Completed', 'Passed',  'Excellent analytical skills.'),
    ( 2,  1, 'Technical',  '2026-09-15 10:00:00', 'Online',    'Microsoft Teams',       'Completed', 'Passed',  'Strong Java and system design knowledge.'),
    ( 3,  1, 'HR',         '2026-09-20 11:00:00', 'In-Person', 'Campus Block A, Room 301', 'Completed', 'Passed', 'Good communication and team fit.'),

    -- App 2: Vivaan → TCS (Interview) — in progress
    ( 4,  2, 'Aptitude',   '2026-09-12 09:00:00', 'Online',    'TCS iON Portal',       'Completed', 'Passed',  'Good problem-solving ability.'),
    ( 5,  2, 'Technical',  '2026-11-05 10:00:00', 'Online',    'Microsoft Teams',       'Scheduled', 'Pending', NULL),

    -- App 3: Priya → TCS (Selected) — completed all rounds
    ( 6,  3, 'Aptitude',   '2026-09-10 09:00:00', 'Online',    'TCS iON Portal',       'Completed', 'Passed',  'Top 5% scorer.'),
    ( 7,  3, 'Technical',  '2026-09-18 10:00:00', 'Online',    'Microsoft Teams',       'Completed', 'Passed',  'Impressive full-stack understanding.'),
    ( 8,  3, 'HR',         '2026-09-22 14:00:00', 'In-Person', 'Campus Block A, Room 301', 'Completed', 'Passed', 'Confident and articulate.'),

    -- App 5: Diya → Infosys (Interview)
    ( 9,  5, 'Aptitude',   '2026-09-25 09:00:00', 'Online',    'Infosys HackWithInfy',  'Completed', 'Passed',  'Strong logical reasoning.'),
    (10,  5, 'Technical',  '2026-11-10 10:00:00', 'Online',    'Zoom Meeting',          'Scheduled', 'Pending', NULL),

    -- App 9: Rohan → Google SDE Intern (Interview)
    (11,  9, 'Technical',  '2026-10-20 10:00:00', 'Online',    'Google Meet',           'Completed', 'Passed',  'Strong DSA fundamentals.'),
    (12,  9, 'Managerial', '2026-11-15 14:00:00', 'Online',    'Google Meet',           'Scheduled', 'Pending', NULL),

    -- App 11: Aarav → Amazon (Interview)
    (13, 11, 'Technical',  '2026-09-20 10:00:00', 'Online',    'Amazon Chime',          'Completed', 'Passed',  'Excellent Python and ML skills.'),

    -- App 15: Arjun → Wipro (Interview)
    (14, 15, 'Aptitude',   '2026-10-15 09:00:00', 'Online',    'Wipro Assessment Portal', 'Completed', 'Passed', 'Decent performance.'),

    -- App 18: Tanvi → Tata Motors (Interview)
    (15, 18, 'Technical',  '2026-11-01 10:00:00', 'In-Person', 'Campus Workshop Lab',   'Scheduled', 'Pending', NULL);

-- ============================================================================
-- OFFERS (5)
-- 2 Accepted, 2 Pending, 1 Declined
-- Accepted offers link to different students with Selected applications
-- ============================================================================
INSERT IGNORE INTO offers
    (offer_id, application_id, student_id, company_id, job_id,
     offer_date, ctc_lpa, offer_status, joining_date)
VALUES
    -- Offer 1: Aarav → TCS (ACCEPTED) — App 1
    (1,  1,  1, 1, 1, '2026-10-01', 7.50,  'Accepted',  '2027-07-01'),

    -- Offer 2: Priya → TCS (ACCEPTED) — App 3
    (2,  3,  8, 1, 1, '2026-10-01', 7.50,  'Accepted',  '2027-07-01'),

    -- Offer 3: Kavya → Amazon (PENDING) — App 13
    (3, 13, 14, 4, 4, '2026-10-10', 12.00, 'Pending',   NULL),

    -- Offer 4: Aarav → Amazon (DECLINED — already accepted TCS) — App 11
    (4, 11,  1, 4, 4, '2026-10-05', 15.00, 'Declined',  NULL),

    -- Offer 5: Priya → Amazon (PENDING) — App 12
    -- Priya already accepted TCS; this is a pending offer she hasn't responded to
    (5, 12,  8, 4, 4, '2026-10-12', 14.00, 'Pending',   NULL);

-- ============================================================================
-- Seed data insertion complete.
-- ============================================================================
