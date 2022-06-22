from django.db import models
from accounts.models import BPUser

class Level(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20,unique=True)
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=20,unique=True)
    def __str__(self):
        return self.name

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

choices_ = (('pending','pending'),('active','active'),('declined','declined'),('expired','expired'),('canceled','canceled'))
class Anchor(models.Model):
    passer =  models.ForeignKey(BPUser, related_name='passer_anchor_table', on_delete=models.CASCADE)
    receiver =  models.ForeignKey(BPUser, related_name='receiver_anchor_table',  on_delete=models.CASCADE, null=True)
    receiver_email = models.EmailField()
    skill = models.ForeignKey(Skill,on_delete=models.CASCADE)
    level = models.ForeignKey(Level,on_delete=models.CASCADE)
    status = models.CharField(choices=choices_, max_length=25, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('passer','receiver_email', 'skill',)
    def __str__(self):
        return self.passer.__str__()

class Profile(models.Model):
    owner = models.OneToOneField('accounts.BPUser', on_delete=models.CASCADE)
    spec = models.TextField()

    def __str__(self):
        return self.owner.email
