from rest_framework import serializers
from .models import Attribute, Profile, Level,Skill
from django.contrib.auth import authenticate
from accounts.models import BPUser

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id','name')

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('id','name')

class AssessmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    skill = SkillSerializer(required=False)
    level = LevelSerializer(required=False)

class AnchorSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    passer = serializers.EmailField(required=False)
    receiver_email = serializers.EmailField()
    skill = serializers.CharField()
    level = serializers.CharField()
    status = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

class BPUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BPUser
        fields = ('email','password')

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'name',)

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('id', 'name',)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('spec',)

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
