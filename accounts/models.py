from django.contrib.auth.models import AbstractUser
from django.db import models
import string
import random

class BPUser(AbstractUser):

    email = models.EmailField(unique = True)

    def initials(self):
        return f"{self.first_name[0:1].upper()}{self.last_name[0:1].upper()}"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

class Invite(models.Model):
    email = models.EmailField(unique = True)
    code = models.CharField(max_length=8, unique=True)
    created_by = models.ForeignKey(BPUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_by = models.ForeignKey(BPUser, null=True, related_name='accepted_by_table', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs) -> None:
        if "code" in kwargs.keys() or len (args) > 0:
            super().__init__(*args, **kwargs)
        else:
            code_ = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            super().__init__(code=code_, **kwargs)

    def __str__(self):
        return self.email