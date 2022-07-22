from os import stat
from urllib import response
from main.models import Opportunity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
import io

class OpportunitiesView(APIView):
    def get(self,request):
        opps = Opportunity.objects.filter(owner=request.user)
        list = []
        for opp in opps:
            y = {
                "id": opp.id,
                "organization_name": opp.job.org_name(),
                "description_url": opp.job.description_url(),
                "status": opp.status(),
                "update_at": opp.updated_at,
            }
            list.append(y)
        return Response(list, status=status.HTTP_200_OK)

class OpportunityView(APIView):
    def put(self, request, id, action):
        try:
            opp = Opportunity.objects.get(id=id)
            if(opp.owner != request.user):
                return Response(None,status=status.HTTP_401_UNAUTHORIZED)
            if action == 'decline':
                opp.decline()
            elif action == 'accept':
                opp.accept()
            elif action == 'close':
                opp.close()
            else:
                return Response({"message":f"unknown action {action}"},status=status.HTTP_400_BAD_REQUEST)
            opp.save()
            return Response(None,status=status.HTTP_200_OK)
        except:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)

        
