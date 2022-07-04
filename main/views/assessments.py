from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.serializers import AssessmentSerializer
from main.models import Skill,Level,Assessment
from rest_framework.parsers import JSONParser
import io
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse

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
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
            a = Assessment( owner=request.user,
                            skill=Skill.objects.get(name=atts['skill']['name']),
                            level=Level.objects.get(name=atts['level']['name']))
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
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
            item = self.get_(id)
            if "skill" in atts:
                item.skill = Skill.objects.get(name=atts['skill']['name'])
            if "level" in atts:
                if "id" in atts['level']:
                    item.level = Level.objects.get(id=atts['level']['id'])
                else:
                    item.level = Level.objects.get(name=atts['level']['name'])
            item.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)