from django.contrib.auth.models import AbstractUser
from django.db import models

class BPUser(AbstractUser):

    email = models.EmailField(unique = True)

    def initials(self):
        return f"{self.first_name[0:1].upper()}{self.last_name[0:1].upper()}"
    
    def fullName(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email