from django.core.management.base import BaseCommand
from accounts.models import BPUser
from main.models import Level, Skill,Attribute,Category
import requests
import re



class Command(BaseCommand):
    help = 'Load some data into a clean DB'

    def handle(self, *args, **options):
        #
        # Attributes
        #
        Category.objects.all().delete()
        Attribute.objects.all().delete()
        category = ''
        with open('./main/management/commands/attributes.txt') as file:
            while (line := file.readline().rstrip()):
                if re.match('^\w',line):
                    category = line.strip()
                    c = Category(name=line.strip())
                    c.save()
                else:
                    print(f"{category},{line.strip()}")
                    Attribute(category=c, name=line.strip()).save()

        #
        # Tech Skills
        #
        list_url = "https://raw.githubusercontent.com/tammer/technology-list/main/list.txt"
        for i in requests.get(list_url).text.split("\n"):
            if len(i) > 0:
                Skill(name=i).save()

        #
        # Levels
        #
        for idx, x in enumerate(['novice','capable','proficient','expert','authority']):
            Level(id=idx+1, name=x).save()

        #
        # Users
        #
        BPUser.objects.create_superuser(username='admin',email='admin@tammer.com',password='123')
        for i in ('ross@quandl.com','najwa@quandl.com'):
            u = BPUser.objects.create_user(
                username="U"+i,
                password="123",
                email=i)