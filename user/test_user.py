import uuid

from django.test import TestCase

from .models import User


class HBBNUserTestCase(TestCase):

    def test_user_create(self):
        email = 'test@test.com'
        username = 'test'
        password = 'test'

        User.objects.create_user(email,
                                 username,
                                 password)
        user = User.objects.get(email=email)

        self.assertTrue(isinstance(user.id, uuid.UUID))
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

        modified_username = 'test2'
        user.username = modified_username
        user.save()

        self.assertNotEqual(user.created_at, user.modified_at)
