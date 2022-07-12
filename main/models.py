from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import BPUser, Invite
import json

class SkillManager(models.Manager):
    def smart_get(self,key):
        try:
            return self.get(id=key)
        except (Skill.DoesNotExist, ValueError):
            try:
                return self.get(name=key)
            except Skill.DoesNotExist:
                return None

class Skill(models.Model):
    name = models.CharField(max_length=120,unique=True)
    objects = SkillManager()
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    def __str__(self):
        return self.name

class Attribute(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    def __str__(self):
        return self.name

class EndorsementManager(models.Manager):
    def highest(self, owner, skill):
        l = -1
        for e in self.filter(owner=owner, skill=skill):
            l = max(l,e.level)
        if l == -1:
            return None
        return l

    def endorsers(self, user):
        rv = []
        for e in self.filter(owner=user).order_by('created_at'):
            if e.counterparty not in rv:
                rv.append(e.counterparty)
        return rv

choices_ = (('pending','pending'),('accepted','accepted'),('declined','declined'),('expired','expired'),('cancelled','cancelled'))
class Anchor(models.Model):
    passer =  models.ForeignKey(BPUser, related_name='passer_anchor_table', on_delete=models.CASCADE)
    receiver =  models.ForeignKey(BPUser, related_name='receiver_anchor_table',  on_delete=models.CASCADE, null=True)
    receiver_invite = models.ForeignKey(Invite, on_delete=models.CASCADE, null=True)
    skill = models.ForeignKey(Skill,on_delete=models.CASCADE)
    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(choices=choices_, max_length=120, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    PENDING = choices_[0][0] 
    ACCEPTED = choices_[1][0]
    DECLINED = choices_[2][0]  
    EXPIRED = choices_[3][0]  
    CANCELLED = choices_[4][0]  
    class Meta:
        unique_together = ('passer','receiver', 'skill',)
        unique_together = ('passer','receiver_invite', 'skill',)

    def receiver_email(self):
        if self.receiver is None:
            return self.receiver_invite.email
        else:
            return self.receiver.email

    def partner(self,user):
        if self.passer == user:
            return self.receiver
        elif self.receiver == user:
            return self.passer
        else:
            raise "user is not the passer or the reseiver"

    def __str__(self):
        return self.passer.__str__()

class Endorsement(models.Model):
    anchor = models.ForeignKey(Anchor, on_delete=models.CASCADE)
    owner = models.ForeignKey(BPUser, related_name='owner_endorsement_table', on_delete=models.CASCADE)
    counterparty = models.ForeignKey(BPUser, related_name='counterparty_endorsement_table', on_delete=models.CASCADE) 
    skill = models.ForeignKey(Skill,on_delete=models.CASCADE) 
    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = EndorsementManager()
 
    class Meta:
        unique_together = ('owner','counterparty', 'skill',)

    def __str__(self):
        return self.skill.name

class Profile(models.Model):
    owner = models.OneToOneField('accounts.BPUser', on_delete=models.CASCADE)
    spec = models.TextField()

    def skills(self):
        rv = []
        for i in json.loads(self.spec)['TechStack']['attributes']:
            rv.append(Skill.objects.get(id=i['id']))
        return rv


class Assessment(models.Model):
    owner =  models.ForeignKey(BPUser, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill,on_delete=models.CASCADE)
    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    class Meta:
        unique_together = ('owner','skill',)

    def __str__(self):
        return self.owner.email

