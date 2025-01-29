from rest_framework import serializers
from .models import Book
from Review.models import Review
from User.serilizer import simpleUserSerializer
class simpleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author' ]
class ReviewSerializer(serializers.ModelSerializer):
    user=simpleUserSerializer(read_only=True)
    book=simpleBookSerializer(read_only=True)
    class Meta:
        model = Review
        fields= [ "book", "user",  "content"]
        read_only_fields= ['user','book']

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

       