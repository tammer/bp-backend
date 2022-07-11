from ..serializers import ProfileSerializer
from ..models import Profile,Assessment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MyProfile(APIView):
    def get_(self,request):
        try:
           return Profile.objects.get( owner=request.user )
        except:
            return None

    def get(self,request, format=None):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        profile = self.get_(request)
        if profile is None:
            return Response('your profile does not exist',status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileSerializer(profile,many=False)
        return Response(serializer.data)

    def delete(self,request,format=None):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        profile = self.get_(request)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, format=None):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        profile = self.get_(request)
        if profile is None:
            profile = Profile(owner=request.user)
        s = ProfileSerializer(profile, data=request.data)
        if s.is_valid():
            s.save()
            defaultLevel = 0
            for skill in profile.skills():
                if not(Assessment.objects.filter(owner=request.user, skill=skill).exists()):
                    Assessment(owner=request.user, skill=skill,level=defaultLevel).save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)