#users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager

from .validators import validate_username

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Доработанная модель пользователя"""
    ROLE_NAME_GUEST = 'guest'
    ROLE_NAME_USER = 'user'
    ROLE_NAME_ADMIN = 'admin'

    ROLES = [
        (ROLE_NAME_GUEST, 'Не авторизованный пользователь'),
        (ROLE_NAME_USER, 'Авторизованный пользователь'),
        (ROLE_NAME_ADMIN, 'Администратотр')
    ]

    username = models.CharField('Имя пользователя', max_length=150, unique=True, blank=False, null=False, validators=(validate_username, ))
    # password = models.CharField('Пароль', max_length=150, blank=False, null=False)
    first_name = models.CharField('Имя', max_length=30, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField('email адрес', unique=True, blank=False, null=False)
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(role_name) for role_name, role_desc in ROLES),
        choices=ROLES,
        default='user')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # # USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'email'
    # EMAIL_FIELD = 'email'

    # def __str__(self):
    #     return self.email

    # REQUIRED_FIELDS = ['email']
    # REQUIRED_FIELDS = ['username']
    # # REQUIRED_FIELDS = ['']
    

    # class Meta:
    #     ordering = ('username', )
    #     verbose_name = 'Пользователь'
    #     verbose_name_plural = 'Пользователи'

        # swappable = 'AUTH_USER_MODEL'


    def __str__(self):
        return f'{self.username} - {self.email}'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



    @property
    def is_administrator(self):
        return (self.role == self.ROLE_NAME_ADMIN or self.is_staff
                or self.is_superuser)

    @property
    def is_user(self):
        return (self.role == self.ROLE_NAME_USER)
