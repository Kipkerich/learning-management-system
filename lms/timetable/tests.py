from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time
from accounts.models import UserProfile, StudentProfile
from courses.models import Course, Unit
from timetable.models import Room, Timetable


class TimetableModuleTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='password123'
        )
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user)
        self.admin_profile.user_type = 'admin'
        self.admin_profile.save()

        self.trainer_user = User.objects.create_user(
            username='trainer1', email='trainer1@test.com', password='password123', first_name='John', last_name='Doe'
        )
        self.trainer_profile, _ = UserProfile.objects.get_or_create(user=self.trainer_user)
        self.trainer_profile.user_type = 'trainer'
        self.trainer_profile.save()

        self.course = Course.objects.create(name='Computer Science', code='CS101', school_fee=1000)
        self.other_course = Course.objects.create(name='Nursing', code='NUR101', school_fee=1200)

        self.unit1 = Unit.objects.create(course=self.course, name='Database Systems', code='CS102')
        self.unit2 = Unit.objects.create(course=self.course, name='Web Development', code='CS103')
        self.other_unit = Unit.objects.create(course=self.other_course, name='Anatomy', code='NUR102')

        self.student_user = User.objects.create_user(
            username='student1', email='student1@test.com', password='password123'
        )
        self.student_user_profile, _ = UserProfile.objects.get_or_create(user=self.student_user)
        self.student_user_profile.user_type = 'student'
        self.student_user_profile.save()

        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_number='ADM001',
            date_of_birth='2000-01-01',
            gender='M',
            course=self.course
        )

        self.room1 = Room.objects.create(name='Lab 1', capacity=30)
        self.room2 = Room.objects.create(name='Hall A', capacity=100)

        self.client = Client()

    def test_room_management(self):
        self.client.login(username='admin', password='password123')

        # Test creating room
        response = self.client.post(reverse('manage_rooms'), {
            'name': 'Lab 2',
            'capacity': 25,
            'description': 'Computer Lab 2'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name='Lab 2').exists())

        # Test editing room
        room = Room.objects.get(name='Lab 2')
        response = self.client.post(reverse('edit_room', kwargs={'pk': room.pk}), {
            'name': 'Lab 2 Updated',
            'capacity': 35,
            'description': 'Updated'
        })
        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertEqual(room.name, 'Lab 2 Updated')

        # Test deleting room
        response = self.client.post(reverse('delete_room', kwargs={'pk': room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(pk=room.pk).exists())

    def test_get_units_by_course_api(self):
        self.client.login(username='admin', password='password123')
        url = reverse('api_get_units') + f'?course_id={self.course.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('units', data)
        self.assertEqual(len(data['units']), 2)

    def test_create_timetable_success(self):
        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('create_timetable'), {
            'course': self.course.id,
            'unit': self.unit1.id,
            'unit_type': 'core',
            'date': '2025-09-01',
            'start_time': '09:00',
            'end_time': '11:00',
            'trainer': self.trainer_user.id,
            'location': self.room1.id,
            'description': 'Database lecture',
            'repeat_count': 1,
            'is_published': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Timetable.objects.filter(course=self.course, unit=self.unit1).exists())

    def test_common_units_combining_allowed(self):
        # Create an initial common unit session
        Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            course=self.course,
            unit=self.unit1,
            unit_type='common',
            subject=self.unit1.name,
            trainer=self.trainer_user,
            location=self.room1
        )

        self.client.login(username='admin', password='password123')
        # Combine another common unit with the same trainer in the same room at the same time
        response = self.client.post(reverse('create_timetable'), {
            'course': self.other_course.id,
            'unit': self.other_unit.id,
            'unit_type': 'common',
            'date': '2025-09-01',
            'start_time': '09:00',
            'end_time': '11:00',
            'trainer': self.trainer_user.id,
            'location': self.room1.id,
            'description': 'Combined common unit lecture',
            'repeat_count': 1,
            'is_published': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Timetable.objects.filter(unit=self.other_unit, unit_type='common').exists())

    def test_common_unit_different_room_fails(self):
        # Create an initial common unit session in room1
        Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            course=self.course,
            unit=self.unit1,
            unit_type='common',
            subject=self.unit1.name,
            trainer=self.trainer_user,
            location=self.room1
        )

        self.client.login(username='admin', password='password123')
        # Try to schedule a common unit in room2 with the same trainer at the same time (trainer cannot be in two rooms)
        response = self.client.post(reverse('create_timetable'), {
            'course': self.other_course.id,
            'unit': self.other_unit.id,
            'unit_type': 'common',
            'date': '2025-09-01',
            'start_time': '09:00',
            'end_time': '11:00',
            'trainer': self.trainer_user.id,
            'location': self.room2.id,
            'description': 'Clash in different room',
            'repeat_count': 1,
            'is_published': True
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Timetable.objects.filter(unit=self.other_unit).exists())

    def test_student_only_views_enrolled_course_units(self):
        # Create a timetable session for CS101 and one for Nursing
        session_cs = Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            course=self.course,
            unit=self.unit1,
            subject=self.unit1.name,
            trainer=self.trainer_user,
            location=self.room1,
            is_published=True
        )
        session_nur = Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(11, 30),
            end_time=time(13, 0),
            course=self.other_course,
            unit=self.other_unit,
            subject=self.other_unit.name,
            trainer=self.trainer_user,
            location=self.room2,
            is_published=True
        )

        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('timetable'))
        self.assertEqual(response.status_code, 200)
        # Check that session_cs is present in dates context, but session_nur is not
        dates = response.context['dates']
        all_sessions = [s for d, list_s in dates for s in list_s]
        self.assertIn(session_cs, all_sessions)
        self.assertNotIn(session_nur, all_sessions)

    def test_trainer_double_booking_prevention(self):
        # Create an initial session
        Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            course=self.course,
            unit=self.unit1,
            subject=self.unit1.name,
            trainer=self.trainer_user,
            location=self.room1
        )

        self.client.login(username='admin', password='password123')
        # Try to book the same trainer at overlapping time (10:00 to 12:00) in room2
        response = self.client.post(reverse('create_timetable'), {
            'course': self.course.id,
            'unit': self.unit2.id,
            'date': '2025-09-01',
            'start_time': '10:00',
            'end_time': '12:00',
            'trainer': self.trainer_user.id,
            'location': self.room2.id,
            'description': 'Overlapping session',
            'repeat_count': 1,
            'is_published': True
        })
        self.assertEqual(response.status_code, 200) # Form re-renders with error
        self.assertFalse(Timetable.objects.filter(unit=self.unit2).exists())

    def test_room_double_booking_prevention(self):
        # Create an initial session with trainer1 in room1
        Timetable.objects.create(
            date=date(2025, 9, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            course=self.course,
            unit=self.unit1,
            subject=self.unit1.name,
            trainer=self.trainer_user,
            location=self.room1
        )

        # Create another trainer
        trainer2 = User.objects.create_user(username='trainer2', password='password123')
        trainer2_profile, _ = UserProfile.objects.get_or_create(user=trainer2)
        trainer2_profile.user_type = 'trainer'
        trainer2_profile.save()

        self.client.login(username='admin', password='password123')
        # Try to book room1 at overlapping time with trainer2
        response = self.client.post(reverse('create_timetable'), {
            'course': self.course.id,
            'unit': self.unit2.id,
            'date': '2025-09-01',
            'start_time': '09:30',
            'end_time': '10:30',
            'trainer': trainer2.id,
            'location': self.room1.id,
            'description': 'Room clash',
            'repeat_count': 1,
            'is_published': True
        })
        self.assertEqual(response.status_code, 200) # Form re-renders with error
        self.assertFalse(Timetable.objects.filter(trainer=trainer2).exists())
