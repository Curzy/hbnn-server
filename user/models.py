import uuid
import os
import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email: str, username: str, password: str=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    MALE = 1
    FEMALE = 2

    GENDER_CHOICES = (
        (MALE, '남'),
        (FEMALE, '여')
    )

    objects = UserManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=60, unique=True)

    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=MALE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'


class UserProfile(models.Model):
    KOREAN = 1
    CHINESE = 2
    JAPANESE = 3
    WESTERN = 4
    VEGETARIAN = 5

    TASTE_CHOICES = (
        (KOREAN, '한식'),
        (CHINESE, '중식'),
        (JAPANESE, '일식'),
        (WESTERN, '양식'),
        (VEGETARIAN, '채식')
    )

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)

    taste = models.SmallIntegerField(choices=TASTE_CHOICES)
    introduction = models.CharField(max_length=128)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


def user_directory_path(username, filename):
    return f'images/{username}/{self.get_filename(filename)}'


def get_filename(username, filename):
    file_extension = os.path.splitext(filename)[1]
    now = datetime.datetime.now()

    return f'{username}-{now.date()}-{now.microsecond}' \
           f'{file_extension}'


class UserPhoto(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    image = models.ImageField(null=True)

    priority = models.PositiveSmallIntegerField(default=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
