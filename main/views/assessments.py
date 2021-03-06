from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.serializers import AssessmentSerializer
from main.models import Endorsement, Profile, Skill,Assessment
from rest_framework.parsers import JSONParser
import io
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from main.utils import highestAnchorLevel

class AssessmentsView(APIView):
    def get(self,request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        # required skills are skills cited in the user's profile OR a skill that has been endorsed
        # required basically means you can't delete it
        try:
            requiredSkills = Profile.objects.get(owner=request.user).skills()
        except:
            requiredSkills = []
        assessments = Assessment.objects.filter(owner=request.user).order_by("id")
        # mark certain assessments as "required".  also set min and max based on if they are endorsed
        for assessment in assessments:
            m = Endorsement.objects.highest(owner=request.user, skill=assessment.skill)
            if m is not None:
                assessment.min_level = max(0,m-20)
                assessment.max_level = min(100,m+20)
                requiredSkills.append(assessment.skill)
            else:
                assessment.min_level = 0
                assessment.max_level = 100
        serializer = AssessmentSerializer(assessments,many=True)
        requiredSkillIDs = list(map(lambda x: x.id, requiredSkills))
        for i in serializer.data:
            if i['skill']['id'] in requiredSkillIDs:
                i['required'] = True
            else:
                i['required'] = False
        return Response(serializer.data)

    def post(self,request):
        if not(request.user.is_authenticated):
            return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = AssessmentSerializer(data=self.request.data,context={ 'request': self.request })
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
            if 'id' in atts['skill']:
                skill = Skill.objects.get(id=atts['skill']['id']) 
            else:
                skill = Skill.objects.get(name=atts['skill']['name']) 
            a = Assessment( owner=request.user,
                            skill=skill,
                            level=atts['level'])
            a.save()
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
        return Response(None, status=status.HTTP_201_CREATED)

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
            assessment = self.get_(id)
            if assessment is None:
                return Response({"message":'assessment no existo'},status=status.HTTP_400_BAD_REQUEST)
            if assessment.owner != request.user:
                return Response({"message":"Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)
            serializer = AssessmentSerializer(assessment,many=False)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            assessment = self.get_(id)
            if assessment.owner != request.user:
                return Response({"message":"Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)
            assessment.delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        if not(request.user.is_authenticated):
           return Response('you dont exist',status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = AssessmentSerializer(data=self.request.data,context={ 'request': self.request })
            atts = JSONParser().parse(io.BytesIO( JSONRenderer().render(serializer.initial_data)))
            assessment = self.get_(id)
            if assessment.owner != request.user:
                return Response({"message":"Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)
            if "skill" in atts:
                if assessment.skill != Skill(**atts['skill']):
                    return Response({"message":"You cannot change the skill; delete and create a new assessment"},status=status.HTTP_400_BAD_REQUEST)
            if "level" in atts:
                assessment.level = atts['level']
            assessment.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)