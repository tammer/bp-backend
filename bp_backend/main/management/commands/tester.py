from django.core.management.base import BaseCommand
from main.models import AnchorInvite
from main.serializers import AnchorInviteSerializer

class Command(BaseCommand):
    def handle(self, *args, **options):
        a = AnchorInvite.objects.all()
        s = AnchorInviteSerializer(a,many=True)
        print(s.data)





        