"""Unit tests for academic eligibility evaluation logic."""
import unittest
from datetime import date, timedelta


class MockEligibilityEvaluator:
    """Pure rule evaluation engine mirroring services.eligibility_service logic for testing."""
    @staticmethod
    def evaluate(student, job, allowed_dept_ids=None, required_skills=None, student_skills=None):
        reasons = []
        if job.get('status') != 'Active':
            reasons.append(f"Job posting is {job.get('status')}")

        deadline = job.get('application_deadline')
        if deadline and deadline < date.today():
            reasons.append("Application deadline has passed")

        if job.get('min_cgpa') is not None and student.get('cgpa', 0) < job['min_cgpa']:
            reasons.append(f"CGPA below minimum ({student.get('cgpa')} < {job['min_cgpa']})")

        if job.get('max_backlogs') is not None and student.get('active_backlogs', 0) > job['max_backlogs']:
            reasons.append(f"Too many backlogs ({student.get('active_backlogs')} > {job['max_backlogs']})")

        if job.get('eligible_grad_year') is not None and student.get('graduation_year') != job['eligible_grad_year']:
            reasons.append("Graduation year mismatch")

        if allowed_dept_ids and student.get('department_id') not in allowed_dept_ids:
            reasons.append("Department not eligible")

        if required_skills:
            st_skills = set(student_skills or [])
            missing = set(required_skills) - st_skills
            if missing:
                reasons.append(f"Missing skills: {', '.join(sorted(missing))}")

        return {
            'eligible': len(reasons) == 0,
            'reasons': reasons if reasons else ['All criteria met']
        }


class TestEligibilityRules(unittest.TestCase):
    def setUp(self):
        self.future_date = date.today() + timedelta(days=30)
        self.past_date = date.today() - timedelta(days=5)

        self.valid_student = {
            'student_id': 1,
            'enrollment_no': 'CS2026001',
            'full_name': 'Aarav Sharma',
            'department_id': 1,
            'graduation_year': 2026,
            'cgpa': 9.20,
            'active_backlogs': 0
        }
        self.student_skills = ['Java', 'SQL', 'Python', 'Data Structures']

        self.standard_job = {
            'job_id': 1,
            'job_title': 'Software Developer',
            'status': 'Active',
            'application_deadline': self.future_date,
            'min_cgpa': 7.00,
            'max_backlogs': 0,
            'eligible_grad_year': 2026
        }
        self.allowed_depts = [1, 2]
        self.required_skills = ['Java', 'SQL']

    def test_fully_qualifying_student(self):
        res = MockEligibilityEvaluator.evaluate(
            self.valid_student, self.standard_job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertTrue(res['eligible'])
        self.assertEqual(res['reasons'], ['All criteria met'])

    def test_ineligible_cgpa_below_minimum(self):
        student = dict(self.valid_student, cgpa=6.50)
        res = MockEligibilityEvaluator.evaluate(
            student, self.standard_job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('CGPA below minimum' in r for r in res['reasons']))

    def test_ineligible_excess_backlogs(self):
        student = dict(self.valid_student, active_backlogs=2)
        res = MockEligibilityEvaluator.evaluate(
            student, self.standard_job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Too many backlogs' in r for r in res['reasons']))

    def test_ineligible_wrong_graduation_year(self):
        student = dict(self.valid_student, graduation_year=2027)
        res = MockEligibilityEvaluator.evaluate(
            student, self.standard_job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Graduation year mismatch' in r for r in res['reasons']))

    def test_ineligible_department_not_allowed(self):
        student = dict(self.valid_student, department_id=4)  # Mech Eng
        res = MockEligibilityEvaluator.evaluate(
            student, self.standard_job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Department not eligible' in r for r in res['reasons']))

    def test_ineligible_missing_required_skills(self):
        res = MockEligibilityEvaluator.evaluate(
            self.valid_student, self.standard_job, self.allowed_depts,
            self.required_skills, ['JavaScript', 'HTML']  # Missing Java and SQL
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Missing skills' in r for r in res['reasons']))

    def test_ineligible_closed_job(self):
        job = dict(self.standard_job, status='Closed')
        res = MockEligibilityEvaluator.evaluate(
            self.valid_student, job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Job posting is Closed' in r for r in res['reasons']))

    def test_ineligible_expired_deadline(self):
        job = dict(self.standard_job, application_deadline=self.past_date)
        res = MockEligibilityEvaluator.evaluate(
            self.valid_student, job, self.allowed_depts,
            self.required_skills, self.student_skills
        )
        self.assertFalse(res['eligible'])
        self.assertTrue(any('Application deadline has passed' in r for r in res['reasons']))


if __name__ == '__main__':
    unittest.main()
