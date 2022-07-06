from django.contrib.auth.models import AbstractUser
from django.db import models

class BPUser(AbstractUser):

    email = models.EmailField(unique = True)

    def initials(self):
        return self.email[0:2].upper()

    def __str__(self):
        return self.email