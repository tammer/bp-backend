from os import stat
from accounts.models import BPUser, Invite
from ..serializers import AttributeSerializer
from ..serializers import LoginSerializer,BPUserSerializer,SkillSerializer
from ..models import Attribute,Category,Profile,Skill,Endorsement,Log
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
import main.views.errors as errors

class friendsView(APIView):
    def get(self, request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        # my endorsers and then add on email addresses in anchors pending
        friends = []
        for e in Endorsement.objects.endorsers(request.user):
            friends.append({
                'first_name':e.first_name,
                'last_name':e.last_name,
                'full_name':e.first_name + " " + e.last_name,
                'display_name':e.first_name + " " + e.last_name + " <" + e.email +">",
                'email':e.email,
                'id':e.email,
                })

        for i in Invite.objects.filter(created_by=request.user):
            friends.append({
                'display_name': i.email,
                'email':i.email,
                'id':i.email})
        return Response(friends,status=status.HTTP_200_OK)

# Not used as far as I can tell July 18, 2022
# class AccountView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         serializer = BPUserSerializer(data=self.request.data,
#             context={ 'request': self.request })
#         serializer.is_valid(raise_exception=True)
#         atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
#         u = BPUser.objects.create_user(username="U"+atts['email'],password=atts['password'],email=atts['email'])
#         Profile(owner=u,spec="{}").save()
#         return JsonResponse({"status":"created"}, status=status.HTTP_201_CREATED)

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
        request.user.auth_token.delete()
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

class LogsView(APIView):
    permission_classes = (permissions.AllowAny,) 
    def post(self,request):
        json = JSONParser().parse(io.BytesIO( JSONRenderer().render(self.request.data)))
        y = Log(value=json['value'])
        y.save()
        return JsonResponse({"value":self.request.data}, status=status.HTTP_200_OK)


class SkillsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request,pattern=None):
        if pattern is None:
            skills = Skill.objects.all()[:30]
        else:
            skills1 = Skill.objects.filter(name__istartswith=pattern).order_by('name')[:20]
            skills2 = Skill.objects.filter(Q(name__icontains=pattern) & ~Q(name__startswith=pattern)).order_by('name')[:20]
            skills = chain(skills1, skills2)
        serializer = SkillSerializer(skills,many=True)
        return Response(serializer.data)

    def post(self,request):
        # if not(request.user.is_authenticated):
        #     return Response(errors.UNAUTHORIZED,status=status.HTTP_401_UNAUTHORIZED)
        serializer = SkillSerializer(data=self.request.data,context={ 'request': self.request })
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
        try:
            existing = Skill.objects.get(name=atts["name"])
            return JsonResponse({"id":existing.id}, status=status.HTTP_200_OK)
        except:
            y = Skill(name=atts["name"])
            y.save();
            return JsonResponse({"id":y.id}, status=status.HTTP_201_CREATED)

class Attributes(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, category_name):
        try:
            category = Category.objects.get(name=category_name)
            attributes = Attribute.objects.filter(category=category)
            serializer = AttributeSerializer(attributes,many=True)
            return Response(serializer.data)
        except:
            return Response({'message': 'bad request. bad category name perhaps? field is case senstive.'},status=status.HTTP_400_BAD_REQUEST)

class CredibilityView(APIView):

    def get(self, request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_401_UNAUTHORIZED)
        endorsements = Endorsement.objects.filter(owner=request.user,is_active=True).count()
        endorsers = Endorsement.objects.filter(owner=request.user, is_active=True).values('counterparty').distinct().count()
        credibility = (endorsements**0.5) * (endorsers**0.5) / (6/1.15)
        rv = {
            'endorsers': endorsers,
            'endorsements': endorsements,
            'credibility': int(round(100. * credibility,0)),
        }
        return Response(rv,status=status.HTTP_200_OK)



