from django.test import TestCase
from django.test import Client
from main.management.commands.setup import Command
from accounts.models import BPUser
from main.models import Skill,Profile
import json
import main.views.errors as errors



def jget(c,path,token=None):
    if token is None:
        r = c.get(path)
    else:
        r = c.get(path,HTTP_AUTHORIZATION=f'Token {token}')
    return (r,json.loads(r.content))

def jpost(c,path,data,token=None):
    if token is None:
        r = c.post(path,data)
    else:
        r = c.post(path,data,HTTP_AUTHORIZATION=f'Token {token}')
    return (r,json.loads(r.content))

def get_token(c):
    (r,j) = jpost(c,'/api-token-auth/',{"username":"najwa@quandl.com","password":"123"})
    return j['token']


class MyTestCase(TestCase):
    def setUp(self):
        Command().handle_(True)
        return super().setUp()

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
        


        
