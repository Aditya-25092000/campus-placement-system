"""Unit tests for backend validation logic."""
import unittest
from routes.student_routes import validate_student


class TestStudentValidation(unittest.TestCase):
    def test_valid_student_passes(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=2026,
            cgpa=8.5,
            active_backlogs=0
        )
        self.assertEqual(len(errors), 0)

    def test_missing_enrollment_no(self):
        errors = validate_student(
            enrollment_no='',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=2026,
            cgpa=8.5,
            active_backlogs=0
        )
        self.assertIn('Enrollment number is required.', errors)

    def test_invalid_email_format(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='invalid-email-string',
            department_id=1,
            graduation_year=2026,
            cgpa=8.5,
            active_backlogs=0
        )
        self.assertIn('Valid email is required.', errors)

    def test_cgpa_out_of_bounds_negative(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=2026,
            cgpa=-1.5,
            active_backlogs=0
        )
        self.assertIn('CGPA must be between 0 and 10.', errors)

    def test_cgpa_out_of_bounds_above_ten(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=2026,
            cgpa=10.5,
            active_backlogs=0
        )
        self.assertIn('CGPA must be between 0 and 10.', errors)

    def test_negative_active_backlogs(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=2026,
            cgpa=8.5,
            active_backlogs=-2
        )
        self.assertIn('Active backlogs cannot be negative.', errors)

    def test_invalid_graduation_year(self):
        errors = validate_student(
            enrollment_no='CS2026001',
            full_name='Aarav Sharma',
            email='aarav@campus.edu',
            department_id=1,
            graduation_year=1995,
            cgpa=8.5,
            active_backlogs=0
        )
        self.assertTrue(any('graduation year' in e.lower() for e in errors))


if __name__ == '__main__':
    unittest.main()
