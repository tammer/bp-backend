from accounts.models import BPUser, Invite
from main.models import Anchor,Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import JSONParser
import io
from rest_framework.renderers import JSONRenderer

from main.serializers import InviteSerializer,SignupSerializer

from rest_framework import permissions

from rest_framework.authtoken.models import Token


class InvitesView(APIView):
    def post(self,request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        serializer = InviteSerializer(data=self.request.data,context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        invite = Invite(email=atts['email'], created_by=request.user)
        invite.save()
        return Response({'code':invite.code}, status=status.HTTP_201_CREATED)


#
# The Invite One
#
class XSignupView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self,request):
        serializer = SignupSerializer(data=self.request.data,context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        try:
            invite = Invite.objects.get(code=atts['code'])
            assert(invite.accepted_by is None)
        except:
            return Response({"error_code":1, "message": "Not a valid invite code (or it was used alreay)"},status=status.HTTP_400_BAD_REQUEST)
        del atts['code']
        atts['username'] = "U" + atts['email']
        u = BPUser.objects.create_user(**atts)
        invite.accepted_by = u
        invite.save()

        # all anchors connected to this invite need to be adjusted to point to the new user
        for anchor in Anchor.objects.filter(receiver_invite=invite):
            anchor.receiver_invite = None
            anchor.receiver = u
            anchor.save()

        token = Token.objects.create(user=u)
        return Response({"token":token.key},status=status.HTTP_201_CREATED)

#
#  No Invite
# !!! (it's just a cut and paste of the above.)
#
class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self,request):
        serializer = SignupSerializer(data=self.request.data,context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        atts['username'] = "U" + atts['email']
        if not BPUser.objects.filter(username=atts['username']).first():
            return Response("email address is in use",status=status.HTTP_400_BAD_REQUEST)
        # remove profile from atts object
        profile = atts['profile']
        del atts['profile']
        u = BPUser.objects.create_user(**atts)
        token = Token.objects.create(user=u)
        
        p = Profile(owner=u)
        p.save()
        p.update(profile)
        return Response({"token":token.key},status=status.HTTP_201_CREATED)
        