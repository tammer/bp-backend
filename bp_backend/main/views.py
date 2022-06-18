from urllib import response
from attr import attributes
from django.shortcuts import render
from yaml import serialize
from .serializers import AttributeSerializer
from .models import Attribute,Category
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Attributes(APIView):
    def get(self, request, category_name):
        try:
            category = Category.objects.get(name=category_name)
            attributes = Attribute.objects.filter(category=category)
            serializer = AttributeSerializer(attributes,many=True)
            return Response(serializer.data)
        except:
            return Response('bad category name perhaps?',status=status.HTTP_400_BAD_REQUEST)

