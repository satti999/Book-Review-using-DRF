from rest_framework import serializers
from .models import User, Profile



class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    role = serializers.CharField(max_length=50)
    class Meta:
        model = User
        fields = ["email", "role", "username", "password"]

    def validate(self, data):
        if 'email' not in data:
            raise serializers.ValidationError({"email": "This field is required."})
        if 'username' not in data:
            raise serializers.ValidationError({"username": "This field is required."})
        if 'password' not in data:
            raise serializers.ValidationError({"password": "This field is required."})
        if 'role' not in data:
            raise serializers.ValidationError({"role": "This field is required."})

        return data

class AuthSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "role", "username", "password"]

    def validate(self, attrs):
        if 'email' not in attrs:
            raise serializers.ValidationError({'email': 'This field is required'})
        if 'role' not in attrs:
            raise serializers.ValidationError({'role': 'This field is required'})
        return attrs

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=50)
    role = serializers.CharField(max_length=50)


    def validate(self, data):
        if 'email' not in data:
            raise serializers.ValidationError({"email": "This field is required."})
        if 'password' not in data:
            raise serializers.ValidationError({"password": "This field is required."})
        if 'role' not in data:
            raise serializers.ValidationError({"role": "This field is required."})

        return data
       
class VerifyAccountSerializer(serializers.Serializer):
        otp = serializers.CharField(max_length=6)
        email = serializers.EmailField(max_length=50)  
def validate(self, data):
        if 'email' not in data:
            raise serializers.ValidationError({"email": "This field is required."})
        if 'otp' not in data:
            raise serializers.ValidationError({"OTP": "This field is required."})


class simpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username' ]



        
class ProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField( required=False, allow_null=True)
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name',  'date_of_birth', 'profile_pic']

   

