from urllib import response
from attr import attributes
from django.shortcuts import render
from yaml import serialize
from .serializers import AttributeSerializer
from .models import Attribute
from rest_framework.views import APIView
from rest_framework.response import Response

class Attributes(APIView):
    def get(self, request):
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes,many=True)
        return Response(serializer.data)
