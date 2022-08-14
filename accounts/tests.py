from django.test import TestCase
from django.test import Client
from main.management.commands.setup import Command
from accounts.models import BPUser,Invite
from main.models import Skill,Profile,Anchor,Assessment,Endorsement,Job,Opportunity
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

def get_token(c,who='najwa'):
    (r,j) = jpost(c,'/api-token-auth/',{"username":f"{who}@quandl.com","password":"123"})
    return j['token']

def najwa():
    return BPUser.objects.get(email='najwa@quandl.com')
def ross():
    return BPUser.objects.get(email='ross@quandl.com')

# The noass thing:  its for backwards compatability on some tests that were created before assessments
# were automaticlaly created in profiles.
def najwa_profile(noass=False, nowrite=False):
    p = Profile.objects.filter(owner=najwa())
    if p.exists():
        return p[0]
    y = {}
    y['TechStack'] = {}
    skill = Skill.objects.all().last()
    z = [{"id":skill.id,"level":22}]
    y['TechStack']['attributes'] = z
    x = Profile(owner=najwa(), spec=y)
    if not(nowrite):
        x.save()
    if not noass:
        Assessment(owner=najwa(), skill=skill, level=22).save()
    return x


class MyTestCase(TestCase):
    def setUp(self):
        Command().handle_(True)
        return super().setUp()


class OpportunityTest(MyTestCase):
    def test(self):
        # gets
        p1 = {"org_name":"ACME Corp", "description_url":"https://www.thestar.com"}
        p2 = {"org_name":"Vandelay Industries", "description_url":"https://www.thestar.com"}
        j1 = Job(owner=ross(), profile=p1)
        j1.save()
        j2 = Job(owner=ross(), profile=p2)
        j2.save()
        o1 = Opportunity(owner=najwa(),job=j1)
        o2 = Opportunity(owner=najwa(),job=j2)
        o1.save()
        o2.save()
        c = Client()
        (r,j) = jget(c,"/opportunities/",token="bad")
        assert(r.status_code==401)
        token = get_token(c)
        (r,j) = jget(c,"/opportunities/",token=token)
        assert(r.status_code==200)

        # puts
        # try to put as Ross, should 401
        (r,j) = jput(c,'/opportunity/1/decline',None,token=get_token(c,"ross"))
        assert(r.status_code==401)
        # put as Najwa
        (r,j) = jput(c,'/opportunity/1/close',None,token=token)
        assert(r.status_code==400)
        (r,j) = jput(c,'/opportunity/1/decline',None,token=token)
        assert(r.status_code==200)
        assert(Opportunity.objects.get(id=1).status() == Opportunity.CLOSED)
        assert(Opportunity.objects.get(id=1).is_declined() == True)
        (r,j) = jput(c,'/opportunity/2/accept',None,token=token)
        assert(r.status_code==200)
        assert(Opportunity.objects.get(id=2).status() == Opportunity.ACCEPTED)
        (r,j) = jput(c,'/opportunity/2/close',None,token=token)
        assert(r.status_code==200)
        assert(Opportunity.objects.get(id=2).status() == Opportunity.CLOSED)
        assert(Opportunity.objects.get(id=2).is_declined() == False)
        (r,j) = jput(c,'/opportunity/2/foo',None,token=token)
        assert(r.status_code == 400)

class InviteTest(MyTestCase):
    def test(self):
        c = Client()
        token = get_token(c)
        # test unauth
        data = {"email":"tammer"}
        (r,j) = jpost(c,"/invites/",data,token="ad")
        assert(r.status_code==401)
        # test ill formatted email
        data = {"email":"tammer"}
        (r,j) = jpost(c,"/invites/",data,token=token)
        assert(r.status_code==400) 
        # test well formatted
        data = {"email":"tammer@quandl.com"}
        (r,j) = jpost(c,"/invites/",data,token=token)
        assert(r.status_code==201) 
        

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

        x = najwa_profile(noass=True) # forces skill to be required because it is in the profile
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
        token = get_token(c)
        # unauthorized
        data = json.dumps( {"spec":"{'TechStack':[1,2,3], 'Role':[1]}"} )
        (r,j) = jput(c,'/profile/',data)
        assert(r.status_code==401)
        
        # authorized, sending junk
        data = "invalid json"
        (r,j) = jput(c,'/profile/',data,token=token)
        assert(r.status_code==400)
        
        # authorized, sending slightly garbled
        data = {"crap":"something else"}
        r = c.put('/profile/',data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==400)
        # now let's send a good profile
        skill = Skill.objects.all().last()
        data = {"Role":{"attributes":[{"id":1}]},'TechStack': {'attributes':[{'id':skill.id, 'level':1}]}}
        r = c.put('/profile/',data,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==200)
        assert(Profile.objects.all().first().spec == data)

        # now let's get it
        #first unauthorized:
        (r,j) = jget(c,'/profile/',token="aaa")
        assert(r.status_code==401)
        # now authorized
        (r,j) = jget(c,'/profile/',token=token)
        assert(r.status_code==200)
        assert(j == {'Role': {'attributes': [{'id': 1, 'name': 'on-site'}]}, 'TechStack': {'attributes': [{'id': 15, 'level': 1, 'name': 'Aerospike'}]}})

        # Confirm skills become assessments
        skill = Skill.objects.all().last()
        spec = {'TechStack': {'attributes':[{'id':skill.id,'level':49}]}}
        r = c.put('/profile/',spec,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==200)
        assert(Profile.objects.all().first().skills()[0] == skill)
        a = Assessment.objects.all().first()
        assert(a.skill == skill)
        assert(a.level == 49)

        # test skills() function
        Profile.objects.all().delete()
        p = najwa_profile(noass=True)
        assert(p.skills()[0]==Skill.objects.all().last())

        # Issue
        Profile.objects.all().delete()
        y = {"Role":{"active":True,"attributes":[]},"WorkModel":{"active":True,"attributes":[]},"Language":{"active":True,"attributes":[]},"Tenure":{"active":True,"attributes":[]},"Location":{"active":True,"attributes":[]},"TechStack":{"active":True,"attributes":[{"id":1,"name":".NET",'level':99}]},"TechAntiStack":{"active":False,"attributes":[]},"OrgSize":{"active":True,"attributes":[]},"OrgType":{"active":True,"attributes":[]},"Industry":{"active":True,"attributes":[]},"Experiential":{"active":True,"attributes":[]},"Salary":{"active":True,"attributes":[{"amount":"100,000","ccy":"USD"}]}}
        r = c.put('/profile/',y,content_type='application/json',HTTP_AUTHORIZATION=f'Token {token}')
        assert(r.status_code==200)

        # skill renamed
        Profile.objects.all().delete()
        p = najwa_profile(noass=True)
        assert(p.get()[Profile.TECHSTACK]['attributes'][0]['name'] == 'Aerospike')

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

# This is for the invite version.  not currently using that.
# class CreateNewUserView(MyTestCase):
#     def test(self):
#         c = Client()
#         data = {"email":"bob@tammer.com","password":"213","code":"bad_code"}
#         # incomple info:
#         (r,j) = jpost(c,"/on         assert(r.status_code==400) 
#         data['first_name'] = "Bob"
#         data['last_name'] = "Smith"
#         (r,j) = jpost(c,"/signup/",data)
#         assert(r.status_code==400)
#         assert(j['error_code'] == 1)
#         assert('message' in j.keys())
#         # now a valid one
#         i = Invite(email="a@b.com",code="123123",created_by=BPUser.objects.get(email='najwa@quandl.com'))
#         i.save()
#         a = Anchor(passer=BPUser.objects.get(email='najwa@quandl.com'),receiver_invite=i,skill=Skill.objects.all().first(),level=99)
#         assert(a.receiver_invite is not None)
#         a.save()
#         data['code'] = "123123"
#         (r,j) = jpost(c,"/signup/",data)
#         assert(r.status_code==201)
#         assert('token' in j.keys())
#         assert(BPUser.objects.get(email='bob@tammer.com').first_name == 'Bob')
#         a = Anchor.objects.all().first()
#         assert(a.receiver_invite is None)
#         assert(a.receiver == BPUser.objects.get(email='bob@tammer.com'))

class SimpleCreateNewUserView(MyTestCase):
    def test(self):
        c = Client()
        data = {"email":"bob@tammer.com"}
        (r,j) = jpost(c,"/signup/",data)
        assert(r.status_code==400) 
        data['password'] = 123
        (r,j) = jpost(c,"/signup/",data)
        assert(r.status_code==400)
        p = najwa_profile(nowrite=True,noass=True)
        data['profile'] = json.dumps(p.get())
        (r,j) = jpost(c,"/signup/",data)
        token = j['token']
        assert(r.status_code==201)
        (r,j) = jget(c,'/profile/',token=token)
        assert(p.get() == j)

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
        n = najwa_profile() 
        (r1,j1) = jget(c,"/profile/",token=j['token'])
        assert(r1.status_code==200)
        assert(j1 == n.get())
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
        


        
