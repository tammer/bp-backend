from django.test import TestCase
from django.test import Client
from main.management.commands.setup import Command
from accounts.models import BPUser,Invite
from main.models import Skill,Profile,Anchor,Assessment,Endorsement
import json
import main.views.errors as errors



def jget(c,path,token=None):
    if token is None:
        r = c.get(path,HTTP_ACCEPT='application/json')
    else:
        r = c.get(path,HTTP_ACCEPT='application/json',HTTP_AUTHORIZATION=f'Token {token}')
    return (r,json.loads(r.content))

def jdelete(c,path,token):
    r = c.delete(path,HTTP_ACCEPT='application/json',HTTP_AUTHORIZATION=f'Token {token}')
    if r.content:
        try:
            return (r,json.loads(r.content))
        except Exception as e:
            print(f"Blowing up. Status code was {r.status_code} Content was:")
            print(r.content)
            raise e
    else:
        return (r,None)


def jpost(c,path,data,token=None):
    if token is None:
        r = c.post(path,data)
    else:
        r = c.post(path,data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
    if r.content:
        return (r,json.loads(r.content))
    else:
        return (r,None)


def jput(c,path,data,token=None):
    if token is None:
        r = c.put(path,data)
    else:
        r = c.put(path,data, content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
    if r.content:
        try:
            return (r,json.loads(r.content))
        except Exception as e:
            print(f"Blowing up. Status code was {r.status_code} Content was:")
            print(r.content)
            raise e
    else:
        return (r,None)

def get_token(c):
    (r,j) = jpost(c,'/api-token-auth/',{"username":"najwa@quandl.com","password":"123"})
    return j['token']

def najwa():
    return BPUser.objects.get(email='najwa@quandl.com')
def ross():
    return BPUser.objects.get(email='ross@quandl.com')

def najwa_profile():
    y = {}
    y['TechStack'] = {}
    skill = Skill.objects.all().last()
    z = [{"id":skill.id}]
    y['TechStack']['attributes'] = z
    x = Profile(owner=najwa(), spec=json.dumps(y))
    x.save()
    return x


class MyTestCase(TestCase):
    def setUp(self):
        Command().handle_(True)
        return super().setUp()

class AssessmentTest(MyTestCase):
    def test_post(self):
        # unauth
        c = Client()
        r = c.post('/assessments/',{})
        assert(r.status_code == 401)

        # auth, legit data
        skill = Skill.objects.all().first()
        user = BPUser.objects.get(email='najwa@quandl.com')
        token = get_token(c)
        data = {"skill":{"id":skill.id},"level":99}
        (r,j) = jpost(c,'/assessments/',data,token=token)
        assert(r.status_code==201)
        assert(Assessment.objects.all().first().owner == user)
        assert(Assessment.objects.all().first().skill == skill)
        assert(Assessment.objects.all().first().level == 99)
        Assessment.objects.all().first().delete()

        # post name instead of id
        skill = Skill.objects.all().last()
        data = {"skill":{"name":skill.name},"level":99}
        (r,j) = jpost(c,'/assessments/',data,token=token)
        assert(r.status_code==201)
        assert(Assessment.objects.all().first().owner == user)
        assert(Assessment.objects.all().first().skill == skill)
        assert(Assessment.objects.all().first().level == 99)

        # post, but the assessment already exists
        (r,j) = jpost(c,'/assessments/',data,token=token)
        assert(r.status_code==400)
    
    def test_get(self):
        a1 = Assessment(owner=BPUser.objects.get(email='najwa@quandl.com'),skill=Skill.objects.get(id=1),level=77)
        a1.save()
        # unauth
        c = Client()
        r = c.get('/assessments/')
        assert(r.status_code == 401)
        # authorized
        token = get_token(c)
        (r,j) = jget(c,'/assessments/',token=token)
        assert(r.status_code==200)
        assert(j[0]['level']==77)
        assert(j[0]['required']==False)

        x = najwa_profile() # forces skill to be required because it is in the profile
        skill1 = Skill.objects.all().last()

        Assessment(owner=najwa(),skill=skill1,level=66).save()
        (r,j) = jget(c,'/assessments/',token=token)
        assert(j[0]['level']==77)
        assert(j[0]['required']==False)
        assert(j[1]['level']==66)
        assert(j[1]['required']==True)

        # ok, now add an endorsement around the first skill (id=1)
        # this should make that skill "required"
        anchor = Anchor(passer=najwa(),receiver=ross(),skill=a1.skill,level=70)
        anchor.save()
        Endorsement(anchor=anchor, owner=najwa(), counterparty=ross(),skill=a1.skill,level=70,is_active=True).save()
        (r,j) = jget(c,'/assessments/',token=token)
        assert(j[0]['level']==77)
        assert(j[0]['required']==True)
        assert(j[1]['level']==66)
        assert(j[1]['required']==True)

    def test_single_path(self):
        
        # PUT
        a1 = Assessment(owner=BPUser.objects.get(email='ross@quandl.com'),skill=Skill.objects.get(id=1),level=77)
        a2 = Assessment(owner=BPUser.objects.get(email='najwa@quandl.com'),skill=Skill.objects.get(id=1),level=77)
        a1.save()
        a2.save()
        c = Client()
        token = get_token(c)
        # unauth
        r = c.put('/assessment/1',{"a":1})
        assert(r.status_code == 401)
        # authorized, but I don't own it.  expect 401
        data={"level":22}
        (r,j) = jput(c,f'/assessment/{a1.id}',data,token=token)
        assert(r.status_code==401)
        # authoirzed, but I am trying to change the skill, should 400
        data={"skill":{"id":4}}
        (r,j) = jput(c,f'/assessment/{a2.id}',data,token=token)
        assert(r.status_code==400)
        # a good request
        assert(a2.level==77)
        data={"level":22}
        (r,j) = jput(c,f'/assessment/{a2.id}',data,token=token)
        assert(r.status_code==200)
        assert(Assessment.objects.get(id=a2.id).level==22)

        # GET
        (r,j) = jget(c,f"/assessment/{a1.id}",token=token)
        assert(r.status_code == 401)
        (r,j) = jget(c,"/assessment/99999",token=token)
        assert(r.status_code == 400)
        (r,j) = jget(c,f"/assessment/{a2.id}",token=token)
        assert(j['level']==22)

        # DELETE
        # bad id
        (r,j) = jdelete(c,"/assessment/999999",token=token)
        assert(r.status_code == 400)
        # not my id
        (r,j) = jdelete(c,f"/assessment/{a1.id}",token=token)
        assert(r.status_code == 401) 
        # bad token
        (r,j) = jdelete(c,f"/assessment/{a2.id}",token="123")
        assert(r.status_code == 401) 
        # legit
        (r,j) = jdelete(c,f"/assessment/{a2.id}",token=token)
        assert(r.status_code == 200)
        assert(Assessment.objects.filter(id=a2.id).first() is None)        

class ProfileView_(MyTestCase):
    def test(self):
        c = Client()
        # unauthorized
        data = json.dumps( {"spec":"{'TechStack':[1,2,3], 'Role':[1]}"} )
        (r,j) = jput(c,'/profile/',data)
        assert(r.status_code==401)
        
        # authorized, sending junk
        token = get_token(c)
        data = "invalid json"
        (r,j) = jput(c,'/profile/',data,token=token)
        assert(r.status_code==400)
        
        # authorized, sending slightly garbled
        data = json.dumps( {"spec":"{'TechStack':[1,2,3], 'Role':99999}"} )
        (r,j) = jput(c,'/profile/',data,token=token)
        assert(r.status_code==400)

        # authorized, sending good data
        data = json.dumps( {"spec":'{"something":"something else"}'} )
        r = c.put('/profile/',data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==200)

        # now let's get it
        (r,j) = jget(c,'/profile/',token=token)
        assert(r.status_code==200)
        assert(json.loads(r.content) == json.loads(data))

        # Confirm skills become assessments
        skill = Skill.objects.all().last()
        spec = {'TechStack': {'attributes':[{'id':skill.id}]}}
        spec_string = json.dumps(spec)
        data = json.dumps( {"spec":spec_string} )
        r = c.put('/profile/',data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==200)
        assert(Profile.objects.all().first().skills()[0] == skill)
        a = Assessment.objects.all().first()
        assert(a.skill == skill)
        assert(a.level == 50)

        # Confirm no overwrite if it is there already
        a.level = 75
        a.save()
        r = c.put('/profile/',data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        a = Assessment.objects.all().first()
        assert(a.level == 75)

class AttributesView_(MyTestCase):
    def test(self):
        c = Client()
        (r,j) = jget(c,"/attributes/Industry/")
        assert(r.status_code==200)
        assert(type(j) == type([]))
        assert(type(j[0]['id']==type(1)))
        assert(type(j[1]['name']==type("string")))

        (r,j) = jget(c,"/attributes/Blah/")
        assert(r.status_code==400)

class CreateNewUserView(MyTestCase):
    def test(self):
        c = Client()
        data = {"email":"bob@tammer.com","password":"213","code":"bad_code"}
        # incomple info:
        (r,j) = jpost(c,"/signup/",data)
        assert(r.status_code==400) 
        data['first_name'] = "Bob"
        data['last_name'] = "Smith"
        (r,j) = jpost(c,"/signup/",data)
        assert(r.status_code==400)
        assert(j['error_code'] == 1)
        assert('message' in j.keys())
        # now a valid one
        i = Invite(email="a@b.com",code="123123",created_by=BPUser.objects.get(email='najwa@quandl.com'))
        i.save()
        a = Anchor(passer=BPUser.objects.get(email='najwa@quandl.com'),receiver_invite=i,skill=Skill.objects.all().first(),level=99)
        assert(a.receiver_invite is not None)
        a.save()
        data['code'] = "123123"
        (r,j) = jpost(c,"/signup/",data)
        assert(r.status_code==201)
        assert('token' in j.keys())
        assert(BPUser.objects.get(email='bob@tammer.com').first_name == 'Bob')
        a = Anchor.objects.all().first()
        assert(a.receiver_invite is None)
        assert(a.receiver == BPUser.objects.get(email='bob@tammer.com'))

class LoginAndLogOutView_(MyTestCase):
    def test_post(self):
        c = Client()
        # Bad logins
        (r,j) = jpost(c,'/api-token-auth/',{"username":"najwa@quandl.com","password":"wrongpw"})
        assert(r.status_code==400)
        (r,j) = jpost(c,'/api-token-auth/',{"username":"najwa@quandl.com"})
        assert(r.status_code==400)
        # Good credentials:
        (r,j) = jpost(c,'/api-token-auth/',{"username":"najwa@quandl.com","password":"123"})
        assert(r.status_code==200)
        assert('token' in j.keys())
        # Check token works.
        Profile(owner=BPUser.objects.get(email='najwa@quandl.com'), spec="filler").save()
        (r1,j1) = jget(c,"/profile/",token=j['token'])
        assert(r1.status_code==200)
        assert(j1['spec'] == 'filler')
        # Now log out
        r1= c.get('/logout/',HTTP_AUTHORIZATION=f'Token {j["token"]}')
        assert(r1.status_code==204)
        # auth call should now fail:
        (r1,j1) = jget(c,"/profile/",token=j['token'])
        assert(r1.status_code==401) 
        # and logout again
        r1 = c.get('/logout/',HTTP_AUTHORIZATION=f'Token {j["token"]}')
        assert(r1.status_code==401)

class SkillsView_(MyTestCase):    
    def test_post(self):
        c = Client()
        (r,j) = jpost(c,'/skills/',{})
        assert(r.status_code==401)
        assert(j == errors.UNAUTHORIZED)

        token = get_token(c)
        data = {"name":"New Skill"}
        (r,j) = jpost(c,'/skills/',data,token=token)
        assert(r.status_code==201)
        assert(j['id']==16)

        data = {"name":"New Skill"} # actually it exists now, so rc should be 201
        (r,j) = jpost(c,'/skills/',data,token=token)
        assert(r.status_code==200)
        assert(j['id']==16)

    def test_get(self):
        c = Client()
        (r,j) = jget(c,'/skills/')
        assert(r.status_code == 200)
        assert(type(j[0]['id']==type(1)))
        assert(type(j[1]['name']==type("string")))

        Skill(name='Zero').save()
        Skill(name='zebra').save()
        Skill(name='Zippy').save()
        Skill(name='aaaZaaa').save()
        (r,j) = jget(c,'/skills/z')
        assert(r.status_code==200)
        expected = [{'id': 16, 'name': 'Zero'}, {'id': 18, 'name': 'Zippy'}, {'id': 17, 'name': 'zebra'}, {'id': 19, 'name': 'aaaZaaa'}]
        assert(j == expected)
        


        
