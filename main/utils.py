from main.models import Level, Anchor
from django.db.models import Q

def highestAnchorLevel(user, skill):
    level = Level.objects.get(id=1) # lowest level
    for anchor in Anchor.objects.filter(Q(passer=user) | Q(receiver=user)).filter(skill=skill):
        if anchor.level.id > level.id:
            level = anchor.level
    return level
