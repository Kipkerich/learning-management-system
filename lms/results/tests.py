from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from results.models import TrainerUnitAssignment, StudentResult
from courses.models import Course, Unit
from accounts.models import Cohort, StudentProfile
from finance.models import CourseFee

class ResultsModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin_res',
            email='admin@example.com',
            password='Password123'
        )
        self.trainer = User.objects.create_user(
            username='trainer_bob',
            first_name='Bob',
            last_name='Trainer',
            email='bob@example.com',
            password='Password123',
            is_staff=True
        )
        if hasattr(self.trainer, 'userprofile'):
            self.trainer.userprofile.user_type = 'trainer'
            self.trainer.userprofile.save()
        self.student_user = User.objects.create_user(
            username='student_alice',
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com',
            password='Password123'
        )

        self.course = Course.objects.create(
            name='Diploma in IT',
            code='DIT',
            school_fee=50000.00
        )
        self.course_fee = CourseFee.objects.create(
            course_name='Diploma in IT',
            total_amount=50000.00
        )
        self.unit = Unit.objects.create(
            course=self.course,
            name='Software Engineering',
            code='DIT101'
        )
        self.cohort = Cohort.objects.create(name='Jan Cohort')

        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_number='ADM/DIT/001',
            date_of_birth='2002-01-01',
            gender='F',
            course=self.course_fee,
            cohort=self.cohort
        )

    def test_create_trainer_assignment(self):
        self.client.login(username='admin_res', password='Password123')
        data = {
            'trainer': self.trainer.pk,
            'course': self.course.pk,
            'unit': self.unit.pk,
            'cohort': self.cohort.pk
        }
        response = self.client.post(reverse('create_assignment'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainerUnitAssignment.objects.filter(trainer=self.trainer, unit=self.unit, cohort=self.cohort).exists())

    def test_trainer_assignment_form_trainer_queryset(self):
        from results.forms import TrainerUnitAssignmentForm
        form = TrainerUnitAssignmentForm()
        trainer_qs = form.fields['trainer'].queryset
        self.assertIn(self.trainer, trainer_qs)
        self.assertNotIn(self.admin, trainer_qs)

    def test_enter_results_as_trainer(self):
        assignment = TrainerUnitAssignment.objects.create(
            trainer=self.trainer,
            unit=self.unit,
            cohort=self.cohort
        )
        self.client.login(username='trainer_bob', password='Password123')
        data = {
            f'cat_{self.student_profile.id}': '25.0',
            f'exam_{self.student_profile.id}': '55.0'
        }
        response = self.client.post(reverse('enter_results', args=[assignment.pk]), data)
        self.assertEqual(response.status_code, 302)

        res = StudentResult.objects.get(student=self.student_profile, unit=self.unit)
        self.assertEqual(float(res.cat_score), 25.0)
        self.assertEqual(float(res.exam_score), 55.0)
        self.assertEqual(res.total_score, 80.0)
        self.assertEqual(res.grade, 'A')

    def test_admin_publish_and_transcript_view(self):
        res = StudentResult.objects.create(
            student=self.student_profile,
            unit=self.unit,
            cohort=self.cohort,
            cat_score=20.0,
            exam_score=50.0,
            is_published=False
        )

        self.client.login(username='admin_res', password='Password123')
        # Toggle publish
        response = self.client.get(reverse('publish_results_toggle', args=[res.pk]))
        self.assertEqual(response.status_code, 302)
        res.refresh_from_db()
        self.assertTrue(res.is_published)

        # View Transcript
        transcript_res = self.client.get(reverse('transcript_detail', args=[self.student_profile.pk]))
        self.assertEqual(transcript_res.status_code, 200)
        self.assertContains(transcript_res, 'OFFICIAL ACADEMIC TRANSCRIPT')
        self.assertContains(transcript_res, 'Software Engineering')

    def test_manage_graduation_eligibility(self):
        self.client.login(username='admin_res', password='Password123')
        data = {
            'is_eligible_for_graduation': True,
            'graduation_status': 'Eligible',
            'graduation_notes': 'Cleared all coursework and fees.'
        }
        response = self.client.post(reverse('manage_graduation', args=[self.student_profile.pk]), data)
        self.assertEqual(response.status_code, 302)

        self.student_profile.refresh_from_db()
        self.assertTrue(self.student_profile.is_eligible_for_graduation)
        self.assertEqual(self.student_profile.graduation_status, 'Eligible')

    def test_student_my_results_only_published(self):
        res_unpublished = StudentResult.objects.create(
            student=self.student_profile,
            unit=self.unit,
            cohort=self.cohort,
            cat_score=20.0,
            exam_score=40.0,
            is_published=False
        )

        self.client.login(username='student_alice', password='Password123')
        response = self.client.get(reverse('student_my_results'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'DIT101')

        # Now publish
        res_unpublished.is_published = True
        res_unpublished.save()

        response = self.client.get(reverse('student_my_results'))
        self.assertContains(response, 'DIT101')
