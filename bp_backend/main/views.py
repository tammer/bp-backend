from urllib import response
from attr import attributes
from django.shortcuts import render
from yaml import serialize

from accounts.models import BPUser
from .serializers import AttributeSerializer,ProfileSerializer,LoginSerializer,BPUserSerializer
from .models import Attribute,Category,Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login, logout
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser

class AccountView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = BPUserSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        BPUser.objects.create_user(username="U"+atts['email'],password=atts['password'],email=atts['email'])
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
            return Response('your profile does not exist',status=status.HTTP_400_BAD_REQUEST)
        s = ProfileSerializer(profile, data=request.data)
        if s.is_valid():
            s.save( owner=request.user)
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)