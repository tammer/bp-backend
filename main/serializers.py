from rest_framework import serializers
from .models import Attribute, Profile, Skill
from django.contrib.auth import authenticate
from accounts.models import BPUser,Invite

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    profile = serializers.JSONField(required=False)
    first_name = serializers.CharField(required=False) 
    last_name = serializers.CharField(required=False)
    code = serializers.CharField(required=False) 

class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ('email',)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id','name')

class AssessmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    skill = SkillSerializer(required=False)
    level = serializers.IntegerField(required=False)
    min_level = serializers.IntegerField(required=False)
    max_level = serializers.IntegerField(required=False)

class AnchorSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    passer = serializers.EmailField(required=False)
    receiver_email = serializers.EmailField()
    skill = serializers.CharField()
    level = serializers.IntegerField(required=False)
    my_level = serializers.IntegerField(required=False)
    confirmable = serializers.BooleanField(required=False)
    confirm_range = serializers.DictField(required=False)
    passer_display_name = serializers.CharField(required=False)
    receiver_display_name = serializers.CharField(required=False)
    passer_first_name = serializers.CharField(required=False)
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
