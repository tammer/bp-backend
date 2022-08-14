from main.models import Anchor,Profile,Skill,Assessment
from django.db.models import Q

def highestAnchorLevel(user, skill):
    level = 0
    for anchor in Anchor.objects.filter(Q(passer=user) | Q(receiver=user)).filter(skill=skill):
        if anchor.level > level:
            level = anchor.level
    return level

def udpate_assessments_from_profile(profile):
    techstack = profile.get()[Profile.TECHSTACK]
    for item in techstack['attributes']:
        skill = Skill.objects.get(id=item['id'])
        ass = Assessment.objects.filter(owner=profile.owner, skill=skill)
        if not(ass.exists()):
            Assessment(owner=profile.owner, skill=skill,level=item['level']).save()
        else:
            a = ass[0]
            a.level = item['level']
            a.save()
