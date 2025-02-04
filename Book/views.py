from django.shortcuts import render
from Book_Review.utils import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Book
from .filter import BookFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from User.models import Profile
from User.authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from .serializer import PublishBookSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class PublishBookViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BookFilter
    parser_classes = [MultiPartParser, FormParser]
    pagination_class =CustomPagination
    search_fields = ['title','author', 'description'] 

    def list(self, request):
        try:
            books = Book.objects.all()
            if not books:
                return Response({'message': 'No book found', 'data':{}}, status=status.HTTP_200_OK)
            book_data = [
            {
                "book_id": book.id,
                "book_title": book.title,
                "book_author": book.author,
                "book_likes": book.likes,
                "book_description": book.description,
                "published_by": book.published_by.username if book.published_by else None,
                "cover_image": book.cover_image.url if book.cover_image else None
            }
            for book in books] 
            return Response({'message': 'Books Retrive successfully',
               'data':book_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  
    def create(self, request):
        try:
            serializer = PublishBookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(published_by=self.request.user)
                return Response({'message': 'Book published successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def retrieve(self, request, pk=None):
        try:
            # search this
            book_id = pk
            book = Book.objects.filter(pk=book_id).first()
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            if book.published_by != request.user:
                return Response({'message': 'You can not access this book','data':{}}, status=status.HTTP_200_OK)
            
            return Response({'message': 'Book Retrive successfully','data':{
                "book_title": book.title,
                "book_author": book.author,
                "book_likes": book.likes,
                "book_description": book.description,
                "published_by": book.published_by.username,
                "cover_image": book.cover_image.url if book.cover_image else None

            }}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, pk=None):
        try:
            book_id = pk
            book = Book.objects.filter(published_by=request.user, pk=book_id).first()
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            if book.published_by != request.user:
                return Response({'message': 'You can not update this book','data':{}}, status=status.HTTP_200_OK)
            serializer = PublishBookSerializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save(publish_by=request.user)
                return Response({'message': 'Book updated successfully','data':serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def partial_update(self, request, pk=None):
            try:
                book_id = pk
                book = Book.objects.filter(published_by=request.user, pk=book_id).first()
                if not book:
                    return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
                if book.published_by != request.user:
                    return Response({'message': 'You can not update this book','data':{}}, status=status.HTTP_200_OK)
                serializer = PublishBookSerializer(book, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(publish_by=request.user)
                    return Response({'message': 'Book updated successfully','data':serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
          
        

    def destroy(self, request, pk=None):
        try:
            book_id = pk
            book = Book.objects.filter(published_by=request.user, pk=book_id).first()
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            book.delete()
            return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    @action(detail=False, methods=['post'],url_path='likebook', url_name='likebook')
    def like_book(self, request):
        try:
            print("user like book")
            user=request.user

            book_id = request.data["book_id"]
            
            if not book_id:
                return Response({'message': 'please provide book id','data':{}}, status=status.HTTP_200_OK)
            book = Book.objects.get(pk=book_id)
            print("book id",book_id)
            print("User id",user)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            user_profile = Profile.objects.get(user=user)  
            if book_id in user_profile.liked_books:
                return Response({'message': 'Book already liked','data':{}}, status=status.HTTP_200_OK)
            a=0
            book.likes += 1
            a+=1
            print("likes",book.likes,'a',a)
            book.save()
            user_profile.liked_books.append(book_id)
            user_profile.save()
            self.notify_publisher(book, user)
            # add the book id in the user profile table
            return Response({'message': 'Book liked successfully','data':{}}, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'],url_path='unlike_book')
    def unlike_book(self, request, pk=None):
        try:
            user=request.user
            book_id = request.data["book_id"]
            if not book_id:
                return Response({'message': 'please provide book id','data':{}}, status=status.HTTP_200_OK)
            book = Book.objects.get(pk=book_id)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            user_profile = Profile.objects.get(user=user)
            if book_id not in user_profile.liked_books:
                return Response({'message': 'Book not liked','data':{}}, status=status.HTTP_200_OK)
            book.likes -= 1
            book.save()
            user_profile.liked_books.remove(book_id)
            user_profile.save()
            return Response({'message': 'Book unliked successfully','data':{}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def notify_publisher(self, book, user):
    # Get the channel layer
        channel_layer = get_channel_layer()
        print(f"Sending notification to publisher {book.published_by.id} by {book.published_by.username}")
        print(f"Message: User {user.username} liked your book: {book.title}")

        # Send a message to the publisher's WebSocket group
        async_to_sync(channel_layer.group_send)(
            f"notifications_{book.published_by.id}",  # Group name for the publisher
            {
                "type": "send_notification",
                "message": f"User {user.username} liked your book: {book.title}",
            },
        )