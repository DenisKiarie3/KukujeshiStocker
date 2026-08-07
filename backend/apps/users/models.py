from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model, extending Django's built-in AbstractUser.
    We're not adding a global 'role' field here — role (owner/staff) is
    contextual per store, and lives on StoreStaff instead, since one
    person could own one store and be staff at another.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username