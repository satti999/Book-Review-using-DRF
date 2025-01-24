from rest_framework import serializers
from .models import User,Book



class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    role = serializers.CharField(max_length=50)

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




class PublishBookSerializer(serializers.ModelSerializer):       
        class Meta:
            model = Book
            fields = ['id','title', 'author', 'description','published_by', ]
            read_only_fields= ['published_by']



        def validate_title(self, value):
            if not value.strip():  # Check if the field is empty or contains only spaces
                raise serializers.ValidationError("Title field is required.")
            return value

        def validate_author(self, value):
            if not value.strip():
                raise serializers.ValidationError("Author field is required.")
            return value

        def validate_description(self, value):
            if not value.strip():
                raise serializers.ValidationError("Description field is required.")
            return value

       
        
       
        

