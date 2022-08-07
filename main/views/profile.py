# from ..serializers import ProfileSerializer
from ..models import Profile,Assessment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.models import Skill


class MyProfile(APIView):
    def get_(self,request):
        try:
           return Profile.objects.get( owner=request.user )
        except:
            return None

    def get(self,request):
        profile = self.get_(request)
        if profile is None:
            return Response({"message":'profile does not exist'},status=status.HTTP_400_BAD_REQUEST)
        p = profile.get()
        for item in p[Profile.TECHSTACK]['attributes']:
            try:
                a = Assessment.objects.get(owner=request.user, skill=Skill.objects.get(id=item['id']))
                item['level'] = a.level
            except:
                item['level'] = None
        return Response(p,status=status.HTTP_200_OK)

    def put(self, request):
        profile = self.get_(request)
        if profile is None:
            profile = Profile(owner=request.user)
        try:
            profile.update(request.data)
            techstack = profile.get()[Profile.TECHSTACK]
            for item in techstack['attributes']:
                skill = Skill.objects.get(id=item['id'])
                ass = Assessment.objects.filter(owner=request.user, skill=skill)
                if not(ass.exists()):
                    Assessment(owner=request.user, skill=skill,level=item['level']).save()
                else:
                    a = ass[0]
                    a.level = item['level']
                    a.save()
            return Response(None, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":str(e)},status=status.HTTP_400_BAD_REQUEST)