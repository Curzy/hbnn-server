import uuid

from django.test import TestCase

from .models import User, UserProfile


class HBBNUserTestCase(TestCase):
    email = 'test@test.com'
    username = 'test'
    password = 'test'
    introduction = '안녕하세요'
    description = '자세한 설명은 생략한다'

    def test_user_create(self):

        User.objects.create_user(self.email,
                                 self.username,
                                 self.password)
        user = User.objects.get(email=self.email)

        self.assertTrue(isinstance(user.id, uuid.UUID))
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.username, self.username)
        self.assertTrue(user.check_password(self.password))

        modified_username = 'test2'
        user.username = modified_username
        user.save()

        self.assertNotEqual(user.created_at, user.modified_at)
        user.refresh_from_db()
        self.assertEqual(user.username, modified_username)

    def test_user_profile_create(self):

        User.objects.create_user(self.email,
                                 self.username,
                                 self.password)

        user = User.objects.get(email=self.email)

        UserProfile.objects.create(user=user, taste=UserProfile.JAPANESE,
                                   introduction=self.introduction,
                                   description=self.description)

        user.refresh_from_db()
        profile = user.userprofile
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.taste, UserProfile.JAPANESE)
        self.assertEqual(profile.introduction, self.introduction)
        self.assertEqual(profile.description, self.description)

        user.delete()
        user = User.objects.filter(email=self.email)

        self.assertEqual(user.exists(), False)
        self.assertEqual(UserProfile.objects.exists(), False)
