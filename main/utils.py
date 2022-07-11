from main.models import Anchor
from django.db.models import Q

def highestAnchorLevel(user, skill):
    level = 0
    for anchor in Anchor.objects.filter(Q(passer=user) | Q(receiver=user)).filter(skill=skill):
        if anchor.level > level:
            level = anchor.level
    return level
