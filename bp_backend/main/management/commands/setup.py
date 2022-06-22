from django.core.management.base import BaseCommand
from accounts.models import BPUser
from main.models import Level, Skill
import requests

class Command(BaseCommand):
    help = 'Load some data into a clean DB'

    def handle(self, *args, **options):




        list_url = "https://raw.githubusercontent.com/tammer/technology-list/main/list.txt"
        for i in requests.get(list_url).text.split("\n"):
            if len(i) > 0:
                Skill(name=i).save()


        for idx, x in enumerate(['novice','capable','proficient','expert','authority']):
            Level(id=idx+1, name=x).save()


        BPUser.objects.create_superuser(username='admin',email='admin@tammer.com',password='123')
        for i in ('ross@quandl.com','najwa@quandl.com'):
            u = BPUser.objects.create_user(
                username="U"+i,
                password="123",
                email=i)