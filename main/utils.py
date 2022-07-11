from main.models import Anchor,Endorsement
from django.db.models import Q

def highestAnchorLevel(user, skill):
    level = 0
    for anchor in Anchor.objects.filter(Q(passer=user) | Q(receiver=user)).filter(skill=skill):
        if anchor.level > level:
            level = anchor.level
    return level

def endorsers(user):
    rv = []
    for e in Endorsement.objects.filter(owner=user).order_by('created_at'):
        if e.counterparty not in rv:
            rv.append(e.counterparty)
    return rv