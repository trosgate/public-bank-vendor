from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, short_name, password=None):

        if not email:
            raise ValueError(_("The given email field is required"))
        if not short_name:
            raise ValueError(_("Username field is required"))
        if not password:
            raise ValueError(_("You must set a valid password"))

        user = self.model(email=self.normalize_email(email), short_name=short_name,)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, email, short_name, password):
        user = self.create_user(email, short_name, password=password)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, short_name, password):
        user = self.create_user(
            email=email, 
            short_name=short_name, 
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user