from accounts.models import BPUser
from ..serializers import AttributeSerializer, LevelSerializer,ProfileSerializer
from ..serializers import LoginSerializer,BPUserSerializer,SkillSerializer
from ..models import Attribute,Category,Profile,Skill,Level
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login, logout
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser
from django.db.models import Q
from itertools import chain

class AccountView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = BPUserSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        u = BPUser.objects.create_user(username="U"+atts['email'],password=atts['password'],email=atts['email'])
        Profile(owner=u,spec="{}").save()
        return JsonResponse({"status":"created"}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return JsonResponse({'sessionid':request.session.session_key})

class LogoutView(APIView):

    def get(self, request, format=None):
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LevelsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        levels = Level.objects.all().order_by('id')
        serializer = LevelSerializer(levels,many=True)
        return Response(serializer.data)

class SkillsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request,pattern=None):
        if pattern is None:
            skills = Skill.objects.all()[:30]
        else:
            skills1 = Skill.objects.filter(name__istartswith=pattern)[:20]
            skills2 = Skill.objects.filter(Q(name__icontains=pattern) & ~Q(name__startswith=pattern))[:20]
            skills = chain(skills1, skills2)
        serializer = SkillSerializer(skills,many=True)
        # time.sleep(3)
        return Response(serializer.data)

class Attributes(APIView):

    permission_classes = (permissions.AllowAny,)

    def get(self, request, category_name):
        try:
            category = Category.objects.get(name=category_name)
            attributes = Attribute.objects.filter(category=category)
            serializer = AttributeSerializer(attributes,many=True)
            return Response(serializer.data)
        except:
            return Response('bad category name perhaps?',status=status.HTTP_400_BAD_REQUEST)

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
            s.save( owner=request.user)
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)