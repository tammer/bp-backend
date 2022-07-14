from accounts.models import BPUser,Invite
from ..serializers import AnchorSerializer
from ..models import Anchor, Endorsement,Skill,Assessment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser
from django.db.models import Q

class AnchorsView(APIView):
    def prettyAnchorView(self,request):
        collapsed = False
        rv = {}
        y = [
            [[Anchor.ACCEPTED],Anchor.objects.filter(Q(passer=request.user) | Q(receiver=request.user)).filter(status=Anchor.ACCEPTED)],
            [["sent",Anchor.PENDING],Anchor.objects.filter(passer=request.user).filter(status=Anchor.PENDING).order_by("created_at")],
            [["sent",Anchor.DECLINED],Anchor.objects.filter(passer=request.user).filter(status=Anchor.DECLINED).order_by("created_at")],
            [["received",Anchor.PENDING],Anchor.objects.filter(receiver=request.user).filter(status=Anchor.PENDING).order_by("created_at")],
            [["received",Anchor.DECLINED],Anchor.objects.filter(receiver=request.user).filter(status=Anchor.DECLINED).order_by("created_at")],
        ]
        for item in y:
            key = item[0]
            anchors = item[1]
            x = {}
            for anchor in anchors:
                if anchor.passer == request.user:
                    counterparty = anchor.receiver_email()
                else:
                    counterparty = anchor.passer.email
                if not(counterparty in x):
                    if(collapsed):
                        x[counterparty] = []
                    else:
                        x[counterparty] = {}
                if( collapsed ):
                    x[counterparty].append({"id": anchor.id, "skill":anchor.skill.name, "level":anchor.level, "originated_by_me":anchor.passer == request.user})
                else:
                    level = anchor.level
                    if not(level in x[counterparty]):
                        x[counterparty][level] = []
                    x[counterparty][level].append({"id": anchor.id, "skill":anchor.skill.name, "originated_by_me":anchor.passer == request.user})
            if len(key) == 1:
                rv[key[0]] = x
            else:
                if key[0] in rv:
                    rv[key[0]][key[1]] = x
                else:
                    rv[key[0]] = {key[1]:x}


        return Response(rv)

    def activePartners(self,user):
        rv = {}
        for anchor in Anchor.objects.filter(Q(passer=user) | Q(receiver=user)).\
          filter(status=Anchor.ACCEPTED).order_by('created_at'):
            rv[anchor.partner(user)] = 0
        return list(rv.keys())

    def getAnchor(self,partner,user, skill):
        try:
            return Anchor.objects.get(passer=partner, receiver=user, skill=skill)
        except:
            try:
                return Anchor.objects.get(receiver=partner, passer=user, skill=skill)
            except:
                return None

    def skillView(self, request):
        try:
            skill = Skill.objects.get(name=request.GET['skill'])
        except:
           return Response(f"No skill called {request.GET['skill']} in DB",status=status.HTTP_400_BAD_REQUEST)
        rv=[]
        for partner in self.activePartners(request.user):
            anchor = self.getAnchor(partner,request.user, skill)
            item = { "initials": partner.initials(),
                     "level": None,
                     "full_name": partner.full_name(),
                     "created_at": None if anchor is None else anchor.created_at
                   }
            if anchor is not None:
                item['level'] = anchor.level.name
            rv.append(item)
        return Response(rv, status=status.HTTP_200_OK)

    def received_view(self, request):
        MARGIN = 15
        def calc(me,cp):
            delta = me - cp
            if delta > 0:
                gamma = (MARGIN - delta)/2
                return {'lb': max(0,cp-gamma), 'ub':min(100,me+gamma)}
            else:
                gamma = (MARGIN + delta)/2
                return {'lb': max(0,me-gamma), 'ub':min(100,cp+gamma)}

        anchors = Anchor.objects.filter(receiver=request.user).filter(Q(status=Anchor.PENDING) | Q(status=Anchor.DECLINED)).order_by('-status','-updated_at')
        for anchor in anchors:
            anchor.passer_display_name = anchor.passer.full_name()
            anchor.passer_first_name = anchor.passer.first_name
            a = Assessment.objects.get_or_none(owner=request.user, skill=anchor.skill)
            if a is None:
                anchor.my_level = None
                anchor.confirmable = True
                anchor.confirm_range = {'lb':max(0,anchor.level-10), 'ub':min(100,anchor.level+10)}
            else:
                anchor.my_level = a.level
                delta = anchor.my_level - anchor.level
                anchor.confirmable = True if delta <= MARGIN and delta >= -MARGIN else False
                if anchor.confirmable:
                    anchor.confirm_range = calc(anchor.my_level, anchor.level)
        serializer = AnchorSerializer(anchors,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def get(self, request, filter=None, format=None):
        # try:
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        if filter is None:
            if request.GET.get('skill'):
                return self.skillView(request)
            else:
                return self.prettyAnchorView(request)
        elif filter == 'sent':
            anchors = Anchor.objects.filter(passer=request.user,status=Anchor.PENDING)
        elif filter == 'received':
            return self.received_view(request)
        elif filter == 'all':
            anchors = Anchor.objects.filter(Q(passer=request.user) | Q(receiver=request.user))
        else:
            return Response('Not a valid path',status=status.HTTP_400_BAD_REQUEST)


        serializer = AnchorSerializer(anchors,many=True)
        return Response(serializer.data)
        # except:
            # return Response('Something went wrong',status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,format=None):
        # try:
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        serializer = AnchorSerializer(data=self.request.data,context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.data)))
        skill = Skill.objects.get(name=atts['skill']) 
        useLevel = Assessment.objects.get(owner=request.user, skill=skill).level
        # is the receiver in the database?
        try:
            u = BPUser.objects.get(email=atts['receiver_email'])
            try:
                ai = Anchor.objects.get(passer=request.user, receiver=u, skill=skill)
                ai.level = useLevel
            except Anchor.DoesNotExist:
                ai = Anchor( passer=request.user, receiver=u, skill=skill, level=useLevel)
        except BPUser.DoesNotExist:
            i = Invite.objects.get_or_create(email=atts['receiver_email'], created_by=request.user)[0]
            try:
                ai = Anchor.objects.get(passer=request.user, receiver_invite=i,skill=skill)
                ai.level = useLevel
            except Anchor.DoesNotExist:
                ai = Anchor( passer=request.user, receiver_invite=i, skill=skill, level=useLevel) 
        ai.save()
        return JsonResponse({"status":"created"}, status=status.HTTP_201_CREATED)
        # except Exception as e:
        #     return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

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
            if anchor.passer != request.user and anchor.receiver != request.user:
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
        if action == 'accept' and item.receiver == request.user:
            item.status = Anchor.ACCEPTED
            # item.receiver = request.user
            # item.receiver_invite = None
            if not(Assessment.objects.filter(owner=request.user, skill=item.skill).exists()):
                Assessment(owner=request.user, skill=item.skill,level=item.level).save()
            Endorsement.objects.create(anchor=item, owner=request.user, counterparty=item.passer, skill=item.skill,level=item.level)
            Endorsement.objects.create(anchor=item, owner=item.passer, counterparty=request.user, skill=item.skill,level=item.level)
        elif action == 'decline' and item.receiver == request.user:
            item.status = Anchor.DECLINED
        elif action == 'cancel' and item.passer == request.user:
            item.status = Anchor.CANCELLED
        else:
            return Response('Not a valid request',status=status.HTTP_400_BAD_REQUEST)
        item.save()
        return JsonResponse({"status":"updated"}, status=status.HTTP_201_CREATED)