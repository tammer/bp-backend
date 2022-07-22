from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import BPUser, Invite
import json
from django.db.models.functions import Now

class Job(models.Model):
    owner =  models.ForeignKey(BPUser, on_delete=models.CASCADE)
    profile = models.JSONField()
    is_active = models.BooleanField(default=True)
    def org_name(self):
        try:
            return self.profile['org_name']
        except:
            return None
    def description_url(self):
        try:
            return self.profile['description_url']
        except:
            return None
    def __str__(self):
        return self.org_name()
            

class Opportunity(models.Model):
    PENDING = 'pending'
    DECLINED = 'declined'
    ACCEPTED = 'accepted'
    CLOSED = 'closed'
    owner =  models.ForeignKey(BPUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True) 
    declined_at = models.DateTimeField(null=True) 
    closed_at = models.DateTimeField(null=True)
    # candidate_report = models.JSONField()
    # recruiter_report = models.JSONField()
    def accept(self):
        assert(self.accepted_at is None)
        assert(self.declined_at is None)
        assert(self.closed_at is None)
        self.accepted_at = Now()
    def decline(self):
        assert(self.accepted_at is None)
        assert(self.declined_at is None)
        assert(self.closed_at is None)
        self.declined_at = Now()
        self.closed_at = Now()
    def close(self):
        assert(self.accepted_at is not None)
        assert(self.declined_at is None)
        assert(self.closed_at is None)
        self.closed_at = Now()
    def status(self):
        if self.closed_at is not None:
            return self.CLOSED
        if self.accepted_at is not None:
            return self.ACCEPTED
        else:
            return self.PENDING
    def is_declined(self):
        return True if self.declined_at is not None else False
    def __str__(self):
        return self.id

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
    # EXPIRED = choices_[3][0]  
    # CANCELLED = choices_[4][0]  
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
        # !!! add owner cannot equal counterpary

    def __str__(self):
        return self.skill.name

class Profile(models.Model):
    ORGANIZATION = 'Organization'
    ROLE = 'Role'
    MODEL = 'Model'
    LANGUAGE = 'Language'
    TENURE = 'Tenure'
    LOCATION = 'Location'
    TECHSTACK = 'TechStack'
    TECHANTISTACK = 'TechAntiStack'
    ORGSIZE = 'OrgSize'
    ORGTYPE = 'OrgType' # breaking change (front end)
    INDUSTRY = 'Industry'
    EXPERENTIAL = 'Experential' # !!! breaking change (front end)
    SALARY = 'Salary'

    valid_keys = {  ORGANIZATION:{"values":None},
                    ROLE: {"values":Attribute},
                    MODEL: {"values":Attribute},
                    LANGUAGE: {"values":Attribute},
                    TENURE: {"values":Attribute},
                    LANGUAGE: {'values':Attribute},
                    TENURE: {'values':Attribute},
                    LOCATION: {'values':None},
                    TECHSTACK: {'values':Skill},
                    TECHANTISTACK: {'values':Skill},
                    ORGSIZE: {'values':None},
                    ORGTYPE: {'values':Attribute},
                    INDUSTRY: {'values':Attribute},
                    EXPERENTIAL: {'values':Attribute},
                    SALARY: {'values':None},}
    owner = models.OneToOneField('accounts.BPUser', on_delete=models.CASCADE)
    spec = models.JSONField(null=True)

    def update(self,profile):
        for key in profile.keys():
            if key not in self.valid_keys.keys():
                raise AttributeError(f"{key} is not a valid key")
        self.spec = profile
        self.save()

    def get(self,refresh_names=True):
        if not refresh_names:
            return self.spec
        rv = self.spec
        for key in rv.keys():
            if self.valid_keys[key]['values'] is not None:
                for item in rv[key]['attributes']:
                    item['name'] = self.valid_keys[key]['values'].objects.get(id=item['id']).name
        return rv

    def skills(self):
        my_spec = self.spec
        if my_spec is None or self.TECHSTACK not in my_spec.keys():
            # spec should be a valid dict with a TechStack entry, but if not, don't fail.
            return []
        rv = []
        for i in my_spec[self.TECHSTACK]['attributes']:
            rv.append(Skill.objects.get(id=i['id']))
        return rv




class AssessmentManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except Assessment.DoesNotExist:
            return None

class Assessment(models.Model):
    owner =  models.ForeignKey(BPUser, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill,on_delete=models.CASCADE)
    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    objects = AssessmentManager()
    class Meta:
        unique_together = ('owner','skill',)

    def __str__(self):
        return self.owner.email

