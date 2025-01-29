from rest_framework import serializers
from .models import Review

from Book.serializer import simpleBookSerializer
from User.serilizer import simpleUserSerializer




class ReviewSerializer(serializers.ModelSerializer):
    user=simpleUserSerializer(read_only=True)
    book=simpleBookSerializer(read_only=True)
    class Meta:
        model = Review
        fields= [ "book", "user",  "content"]
        read_only_fields= ['user','book']