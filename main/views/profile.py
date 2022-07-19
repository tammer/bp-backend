from ..serializers import ProfileSerializer
from ..models import Profile,Assessment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import main.views.errors as errors

from rest_framework.parsers import JSONParser
import io
from rest_framework.renderers import JSONRenderer

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

    # Why would we ever need this?
    # def delete(self,request,format=None):
    #     if not(request.user.is_authenticated):
    #        return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
    #     profile = self.get_(request)
    #     profile.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, format=None):
        profile = self.get_(request)
        if profile is None:
            profile = Profile(owner=request.user)
        serializer = ProfileSerializer(data=self.request.data,context={ 'request': self.request })
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
        profile.spec = atts['spec'] # atts['spec'] is just a string (blob)
        if profile.is_valid():
            profile.save()
            defaultLevel = 50
            for skill in profile.skills():
                if not(Assessment.objects.filter(owner=request.user, skill=skill).exists()):
                    Assessment(owner=request.user, skill=skill,level=defaultLevel).save()
            return Response(None, status=status.HTTP_200_OK)
        else:
            return Response({'message':'profile is ill formatted. is the JSON valid?'}, status=status.HTTP_400_BAD_REQUEST)