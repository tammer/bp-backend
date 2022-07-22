# from ..serializers import ProfileSerializer
from ..models import Profile,Assessment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import main.views.errors as errors

from rest_framework.parsers import JSONParser
import json
from rest_framework.renderers import JSONRenderer

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
        return Response(profile.get(),status=status.HTTP_200_OK)

    def put(self, request):
        profile = self.get_(request)
        if profile is None:
            profile = Profile(owner=request.user)
        try:
            profile.update(request.data)
            defaultLevel = 50
            for skill in profile.skills():
                if not(Assessment.objects.filter(owner=request.user, skill=skill).exists()):
                    Assessment(owner=request.user, skill=skill,level=defaultLevel).save()
            return Response(None, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":str(e)},status=status.HTTP_400_BAD_REQUEST)