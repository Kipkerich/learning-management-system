from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Unit

class CoursesAppTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='Password123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='Password123'
        )

        self.course = Course.objects.create(
            name='Diploma in IT',
            code='DIT',
            description='Information Technology Course',
            school_fee=45000.00
        )
        self.unit = Unit.objects.create(
            course=self.course,
            name='Database Systems',
            code='DIT201',
            description='Relational databases'
        )

    def test_course_list_access(self):
        self.client.login(username='admin_user', password='Password123')
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diploma in IT')

    def test_course_sync_with_course_fee(self):
        from finance.models import CourseFee
        new_course = Course.objects.create(
            name='Certificate in Health Systems',
            code='CHS101',
            school_fee=45000.00
        )
        fee = CourseFee.objects.filter(course_name='Certificate in Health Systems').first()
        self.assertIsNotNone(fee)
        self.assertEqual(fee.total_amount, 45000.00)

    def test_course_detail_view(self):
        self.client.login(username='admin_user', password='Password123')
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Database Systems')

    def test_create_course(self):
        self.client.login(username='admin_user', password='Password123')
        data = {
            'name': 'Certificate in Cyber Security',
            'code': 'CCS',
            'description': 'Security fundamentals',
            'school_fee': 35000.00
        }
        response = self.client.post(reverse('create_course'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(code='CCS').exists())

    def test_add_unit_to_course(self):
        self.client.login(username='admin_user', password='Password123')
        data = {
            'name': 'Network Security',
            'code': 'DIT202',
            'description': 'Firewalls and VPNs'
        }
        response = self.client.post(reverse('add_unit', args=[self.course.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Unit.objects.filter(code='DIT202', course=self.course).exists())

    def test_set_course_fee(self):
        self.client.login(username='admin_user', password='Password123')
        data = {
            'course': self.course.pk,
            'school_fee': 50000.00
        }
        response = self.client.post(reverse('set_course_fee'), data)
        self.assertEqual(response.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(float(self.course.school_fee), 50000.00)

    def test_non_staff_redirect(self):
        self.client.login(username='student_user', password='Password123')
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 302)
