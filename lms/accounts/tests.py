from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Cohort, StudentProfile
from finance.models import CourseFee

class CohortAndRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@example.com',
            password='Password123'
        )
        self.course_fee = CourseFee.objects.create(
            course_name='Diploma in Nursing',
            total_amount=50000.00,
            description='Nursing course fee'
        )
        self.cohort = Cohort.objects.create(
            name='Jan Cohort',
            description='January Intake'
        )

    def test_cohort_list_view(self):
        self.client.login(username='admin_test', password='Password123')
        response = self.client.get(reverse('cohort_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jan Cohort')

    def test_create_cohort(self):
        self.client.login(username='admin_test', password='Password123')
        data = {
            'name': 'May Cohort',
            'description': 'May Intake'
        }
        response = self.client.post(reverse('create_cohort'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cohort.objects.filter(name='May Cohort').exists())

    def test_student_registration_with_cohort(self):
        self.client.login(username='admin_test', password='Password123')
        user_data = {
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }
        profile_data = {
            'admission_number': 'ADM/2026/001',
            'course': self.course_fee.pk,
            'cohort': self.cohort.pk,
            'enrollment_date': '2026-01-15',
            'phone_number': '+254712345678',
            'id_number': 12345678,
            'date_of_birth': '2002-05-10',
            'gender': 'M',
            'address': 'Nairobi, Kenya',
            'marital_status': 'Single',
            'nationality': 'Kenyan',
            'former_high_school': 'Alliance High School',
            'parent_primary_name': 'Jane Doe',
            'parent_primary_phone': '+254700000000',
            'parent_secondary_name': '',
            'parent_secondary_phone': ''
        }
        post_data = {**user_data, **profile_data}
        response = self.client.post(reverse('register_student'), post_data)
        if response.status_code != 302:
            print("User Form Errors:", response.context['user_form'].errors if 'user_form' in response.context else None)
            print("Profile Form Errors:", response.context['profile_form'].errors if 'profile_form' in response.context else None)
        self.assertEqual(response.status_code, 302)

        student = StudentProfile.objects.get(admission_number='ADM/2026/001')
        self.assertEqual(student.cohort, self.cohort)
        self.assertEqual(student.address, 'Nairobi, Kenya')

    def test_student_directory_grouping(self):
        self.client.login(username='admin_test', password='Password123')
        student_user = User.objects.create_user(
            username='jane_student',
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        StudentProfile.objects.create(
            user=student_user,
            admission_number='ADM/2026/002',
            date_of_birth='2001-01-01',
            gender='F',
            course=self.course_fee,
            cohort=self.cohort,
            phone_number='+254722222222',
            address='Mombasa, Kenya'
        )

        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diploma in Nursing')
        self.assertContains(response, 'Jan Cohort')
        self.assertContains(response, 'Jane Smith')

    def test_edit_student_profile(self):
        self.client.login(username='admin_test', password='Password123')
        student_user = User.objects.create_user(
            username='edit_student',
            first_name='Original',
            last_name='Name',
            email='edit@example.com'
        )
        student = StudentProfile.objects.create(
            user=student_user,
            admission_number='ADM/2026/003',
            date_of_birth='2000-01-01',
            gender='M',
            course=self.course_fee,
            cohort=self.cohort,
            phone_number='+254711111111',
            address='Nakuru'
        )

        # GET edit student
        res_get = self.client.get(reverse('edit_student', kwargs={'pk': student.pk}))
        self.assertEqual(res_get.status_code, 200)

        # POST edit student
        res_post = self.client.post(reverse('edit_student', kwargs={'pk': student.pk}), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'admission_number': 'ADM/2026/003-UPDATED',
            'course': self.course_fee.pk,
            'cohort': self.cohort.pk,
            'enrollment_date': '2026-01-15',
            'phone_number': '+254799999999',
            'id_number': 99999999,
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'marital_status': 'Single',
            'nationality': 'Kenyan',
            'former_high_school': 'Central High',
            'address': 'Eldoret, Kenya',
            'parent_primary_name': 'Parent Name',
            'parent_primary_phone': '+254700000000',
            'parent_secondary_name': '',
            'parent_secondary_phone': ''
        })
        self.assertEqual(res_post.status_code, 302)

        student.refresh_from_db()
        student_user.refresh_from_db()
        self.assertEqual(student_user.first_name, 'Updated')
        self.assertEqual(student.admission_number, 'ADM/2026/003-UPDATED')
        self.assertEqual(student.address, 'Eldoret, Kenya')

    def test_admin_user_type_permissions(self):
        # Create user with user_type='admin'
        admin_staff = User.objects.create_user(
            username='admin_staff_type',
            email='adminstaff@example.com',
            password='Password123',
            is_staff=True
        )
        if hasattr(admin_staff, 'userprofile'):
            admin_staff.userprofile.user_type = 'admin'
            admin_staff.userprofile.save()

        self.client.login(username='admin_staff_type', password='Password123')

        # Test student directory access
        res = self.client.get(reverse('student_list'))
        self.assertEqual(res.status_code, 200)

        # Test user list access
        res_users = self.client.get(reverse('user_list'))
        self.assertEqual(res_users.status_code, 200)
