from unicodedata import category
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    def __str__(self):
        return self.name

class Attribute(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name