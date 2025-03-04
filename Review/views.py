from django.shortcuts import render
from book_review.utils import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import Review
from Book.models import Book
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from User.authentication import JWTAuthentication 

from rest_framework.permissions import IsAuthenticated
from .serializer import ReviewSerializer


# Create your views here.


class ReviewViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 
    pagination_class =CustomPagination
    

    def create(self, request, pk=None):
        book_id = request.query_params.get('book_id')
        user=request.user
        try:
            book = Book.objects.get(pk=book_id)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            if book.published_by==user:
                return Response({'message':'you can not comment on your book'},status=status.HTTP_200_OK)
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user,book=book)
                self.notify_publisher(book, user)
                return Response({'message': 'Review created successfully','data':{
                    "book_title": book.title,
                    "book_author": book.author,
                    "comment_by": serializer.data['user']['username'],
                    "comment": serializer.data['content'],

                }}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        try:
            book_id = request.query_params.get('book_id')
            book = Book.objects.get(pk=book_id)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            reviews = Review.objects.filter(book=book)
            if not reviews:
                return Response({'message': 'No review found','data':{}}, status=status.HTTP_200_OK)
            # return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Review Retrive successfully','data': {
                "book_title": book.title,
                "book_author": book.author,
                "reviews": [
                    {   
                        "id": item.id,
                        "user_name": item.user.username,
                        "comments": item.content

                    }
                    for item in reviews
                ]
                }}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        try:
            review_id = pk
            review= Review.objects.filter(pk=review_id).first()
            if not review:
                return Response({'message': 'No comment found','data':{}}, status=status.HTTP_200_OK)
            return Response({'message':'Review Retrive successfully','data':{
                "book_title": review.book.title,
                "book_author": review.book.author,
                "user_name": review.user.username,
                "comments": review.content
            } },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def update(self, request, pk=None):
        try:
           review_id = request.query_params.get('review_id')
           review= Review.objects.filter(pk=review_id).first()
           if not review:
               return Response({'message': 'No comment found','data':{}}, status=status.HTTP_200_OK)
           serializer=ReviewSerializer(data=request.data)
           if serializer.is_valid:
               serializer.save()
               return Response({'message':'Your Review is update','data':serializer.data},status=status.HTTP_200_OK)
           else:
               return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def destroy(self, request,pk=None):
        try:
            review_id = request.query_params.get('review_id')
            review= Review.objects.get(pk=review)
            if not review:
               return Response({'message': 'No comment found','data':{}}, status=status.HTTP_200_OK)
            review.delete()
            return Response({'message': 'Your review is  deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def notify_publisher(self, user,book):
           channel_layer = get_channel_layer()
           async_to_sync(channel_layer.group_send)(
                f"notifications_{book.published_by.id}",
                {
                 "type": "send_notification",
                  "message": f"User {user.username} commented on your book: {book.title}",
                },
               
           )
          
        
            
        