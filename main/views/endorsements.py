# from accounts.models import BPUser
from ..models import Skill,Endorsement
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class EndorsementView(APIView):
    def get_(self,id):
        try:
           return Endorsement.objects.get( id=id )
        except:
            return None

    def put(self,request,action, id):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        if id is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        e = self.get_(id)
        if e is None:
            return Response('endorsement no existo',status=status.HTTP_400_BAD_REQUEST)
        if action == 'enable' or action == 'activate':
            e.is_active = True
        elif action == 'disable' or action == 'deactivate':
            e.is_active = False
        else:
            return Response(f'unknown action: {action}',status=status.HTTP_400_BAD_REQUEST)
        e.save()
        return Response('ok',status=status.HTTP_200_OK)

        
            


class EndorsementsView(APIView):
    def get(self, request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        if request.GET.get('skill') is None:
            return Response("not implemented",status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return self.filtered_get(request)


    def filtered_get(self, request):
        skill = Skill.objects.smart_get(request.GET['skill'])
        if skill is None:
            return Response(f"No skill: {request.GET['skill']} in DB",status=status.HTTP_400_BAD_REQUEST) 
        rv=[]
        for cp in Endorsement.objects.endorsers(request.user):
            endorsement = Endorsement.objects.filter(owner=request.user, counterparty=cp, skill=skill, is_active=True).first()
            item = { "initials": cp.initials(),
                     "level": None,
                     "full_name": cp.full_name(),
                     "created_at": None if endorsement is None else endorsement.created_at
                   }
            if endorsement is not None:
                item['level'] = endorsement.level
            rv.append(item)
        return Response(rv, status=status.HTTP_200_OK)