from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, StudentProfile
from courses.models import Course
from resources.models import Resource
from resources.forms import ResourceForm


class ResourcePermissionsAndFormTests(TestCase):
    def setUp(self):
        # Create courses
        self.course1 = Course.objects.create(name="Computer Science", code="CS101")
        self.course2 = Course.objects.create(name="Business Information Technology", code="BIT101")

        # Create admin user
        self.admin_user = User.objects.create_user(username="admin_user", password="password123")
        self.admin_user.userprofile.user_type = 'admin'
        self.admin_user.userprofile.save()

        # Create trainer user
        self.trainer_user = User.objects.create_user(username="trainer_user", password="password123")
        self.trainer_user.userprofile.user_type = 'trainer'
        self.trainer_user.userprofile.save()

        # Create student 1 (in Course 1)
        self.student1_user = User.objects.create_user(username="student1", password="password123")
        self.student1_user.userprofile.user_type = 'student'
        self.student1_user.userprofile.save()
        self.student1_profile = StudentProfile.objects.create(
            user=self.student1_user,
            admission_number="ADM001",
            date_of_birth="2000-01-01",
            gender="M",
            course=self.course1
        )

        # Create student 2 (in Course 2)
        self.student2_user = User.objects.create_user(username="student2", password="password123")
        self.student2_user.userprofile.user_type = 'student'
        self.student2_user.userprofile.save()
        self.student2_profile = StudentProfile.objects.create(
            user=self.student2_user,
            admission_number="ADM002",
            date_of_birth="2000-01-01",
            gender="F",
            course=self.course2
        )

        self.client = Client()

    def test_admin_can_add_resource(self):
        """Test that admin users can create resources and select courses."""
        self.client.login(username="admin_user", password="password123")

        url = reverse("add_resource")
        data = {
            "title": "Admin Resource CS",
            "description": "Resource created by admin",
            "resource_type": "link",
            "url": "https://example.com/cs-doc",
            "courses": [self.course1.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        resource = Resource.objects.get(title="Admin Resource CS")
        self.assertEqual(resource.uploaded_by, self.admin_user)
        self.assertIn(self.course1, resource.courses.all())

    def test_admin_can_edit_and_delete_resource(self):
        """Test that admin users can edit and delete resources."""
        resource = Resource.objects.create(
            title="Trainer Resource",
            description="Created by trainer",
            resource_type="link",
            url="https://example.com/trainer",
            uploaded_by=self.trainer_user
        )
        resource.courses.add(self.course1)

        self.client.login(username="admin_user", password="password123")

        # Admin edits resource
        edit_url = reverse("edit_resource", kwargs={"pk": resource.pk})
        edit_data = {
            "title": "Trainer Resource Updated by Admin",
            "description": "Updated desc",
            "resource_type": "link",
            "url": "https://example.com/updated",
            "courses": [self.course1.id, self.course2.id]
        }
        response = self.client.post(edit_url, edit_data)
        self.assertEqual(response.status_code, 302)

        resource.refresh_from_db()
        self.assertEqual(resource.title, "Trainer Resource Updated by Admin")
        self.assertEqual(resource.courses.count(), 2)

        # Admin deletes resource
        delete_url = reverse("delete_resource", kwargs={"pk": resource.pk})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resource.objects.filter(pk=resource.pk).exists())

    def test_form_validation_errors(self):
        """Test that form clearly reports errors when fields/courses are missing."""
        # 1. Missing courses
        form = ResourceForm(data={
            "title": "Test Title",
            "resource_type": "link",
            "url": "https://example.com",
            "courses": []
        })
        self.assertFalse(form.is_valid())
        self.assertIn("courses", form.errors)

        # 2. Missing link URL for link resource type
        form = ResourceForm(data={
            "title": "Test Link",
            "resource_type": "link",
            "url": "",
            "courses": [self.course1.id]
        })
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)

        # 3. Neither file nor URL
        form = ResourceForm(data={
            "title": "Test Other",
            "resource_type": "other",
            "courses": [self.course1.id]
        })
        self.assertFalse(form.is_valid())
        self.assertTrue("file" in form.errors or "url" in form.errors)

    def test_student_course_visibility_filtering(self):
        """Test that students only see resources assigned to their course."""
        # Resource for Course 1
        r1 = Resource.objects.create(
            title="CS Resource Only",
            resource_type="link",
            url="https://example.com/cs",
            uploaded_by=self.admin_user
        )
        r1.courses.add(self.course1)

        # Resource for Course 2
        r2 = Resource.objects.create(
            title="BIT Resource Only",
            resource_type="link",
            url="https://example.com/bit",
            uploaded_by=self.admin_user
        )
        r2.courses.add(self.course2)

        # Student 1 logs in (Course 1)
        self.client.login(username="student1", password="password123")
        res_list = self.client.get(reverse("resources"))
        self.assertContains(res_list, "CS Resource Only")
        self.assertNotContains(res_list, "BIT Resource Only")

        detail_r1 = self.client.get(reverse("resource_detail", kwargs={"pk": r1.pk}))
        self.assertEqual(detail_r1.status_code, 200)

        detail_r2 = self.client.get(reverse("resource_detail", kwargs={"pk": r2.pk}))
        self.assertEqual(detail_r2.status_code, 404)

        # Student 2 logs in (Course 2)
        self.client.login(username="student2", password="password123")
        res_list2 = self.client.get(reverse("resources"))
        self.assertContains(res_list2, "BIT Resource Only")
        self.assertNotContains(res_list2, "CS Resource Only")
