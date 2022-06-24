from urllib import response
from attr import attributes
from django.shortcuts import render
from yaml import serialize

from accounts.models import BPUser
from .serializers import AnchorSerializer, AttributeSerializer,ProfileSerializer
from .serializers import LoginSerializer,BPUserSerializer,AssessmentSerializer
from .models import Attribute,Category,Profile,Anchor,Skill,Level,Assessment
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

class AssessmentsView(APIView):
    def get(self,request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        assessments = Assessment.objects.filter(owner=request.user)
        serializer = AssessmentSerializer(assessments,many=True)
        return Response(serializer.data)
    def post(self,request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = AssessmentSerializer(data=self.request.data,context={ 'request': self.request })
            serializer.is_valid(raise_exception=True)
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
            a = Assessment( owner=request.user,
                            skill=Skill.objects.get(name=atts['skill']),
                            level=Level.objects.get(name=atts['level']))
            a.save()
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"status":"created"}, status=status.HTTP_201_CREATED)

class AssessmentView(APIView):
    def get_(self,id):
        try:
           return Assessment.objects.get( id=id )
        except:
            return None

    def get(self,request,id):
        try:
            if not(request.user.is_authenticated):
                return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
            if id is None:
                return Response(status=status.HTTP_204_NO_CONTENT)
            assessment = self.get_(id)
            if assessment is None:
                return Response('assessment no existo',status=status.HTTP_400_BAD_REQUEST)
            serializer = AssessmentSerializer(assessment,many=False)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            item = self.get_(id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = AssessmentSerializer(data=self.request.data,context={ 'request': self.request })
            serializer.is_valid(raise_exception=True)
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
            item = self.get_(id)
            if atts['skill'] is not None:
                item.skill = Skill.objects.get(name=atts['skill'])
            if atts['level'] is not None:
                item.level = Level.objects.get(name=atts['level'])
            item.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

class AnchorsView(APIView):
    def get(self, request, filter=None, format=None):
        try:
            if not(request.user.is_authenticated):
                return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
            if filter is None:
                anchors = Anchor.objects.filter(Q(passer=request.user) | Q(receiver=request.user)).filter(status='active')
            elif filter == 'sent':
                anchors = Anchor.objects.filter(passer=request.user,status='pending')
            elif filter == 'received':
                anchors = Anchor.objects.filter(receiver_email=request.user.email,status='pending')
            elif filter == 'all':
                anchors = Anchor.objects.filter(Q(passer=request.user) | Q(receiver_email=request.user.email))
            else:
                return Response('Not a valid path',status=status.HTTP_400_BAD_REQUEST)


            serializer = AnchorSerializer(anchors,many=True)
            return Response(serializer.data)
        except:
            return Response('Something went wrong',status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,filter,format=None):
        try:
            if not(request.user.is_authenticated):
                return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
            serializer = AnchorSerializer(data=self.request.data,context={ 'request': self.request })
            serializer.is_valid(raise_exception=True)
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
            ai = Anchor( passer=request.user,
                        receiver_email=atts['receiver_email'],
                        skill=Skill.objects.get(name=atts['skill']),
                        level=Level.objects.get(name=atts['level']))
            ai.save()
            return JsonResponse({"status":"created"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

class AnchorView(APIView):
    def get_(self,id):
        try:
           return Anchor.objects.get( id=id )
        except:
            return None
    def get(self,request,id=None,action=None,format=None):
        # action is not used; just here so the DRF web helper works in testing
        try:
            if not(request.user.is_authenticated):
                return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
            if id is None:
                return Response(status=status.HTTP_204_NO_CONTENT)
            anchor = self.get_(id)
            if anchor is None:
                return Response('anchor no existo',status=status.HTTP_400_BAD_REQUEST)
            if anchor.passer != request.user and anchor.receiver_email != request.user.email:
                return Response('Not for you to see',status=status.HTTP_400_BAD_REQUEST)
            serializer = AnchorSerializer(anchor,many=False)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id,format=None):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        item = self.get_(id)
        if item.passer != request.user:
                return Response('You are being naughty',status=status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id, action,format=None):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        item = self.get_(id)
        if action == 'accept' and item.receiver_email == request.user.email:
            item.status = 'active'
            item.receiver = request.user
        elif action == 'decline' and item.receiver_email == request.user.email:
            item.status = 'declined'
        elif action == 'cancel' and item.passer == request.user:
            item.status = 'cancelled'
        else:
            return Response('Not a valid request',status=status.HTTP_400_BAD_REQUEST)
        item.save()
        return JsonResponse({"status":"updated"}, status=status.HTTP_201_CREATED)

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