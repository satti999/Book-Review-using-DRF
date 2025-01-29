from django.shortcuts import render
from Book_Review.utils import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Book
from User.models import Profile
from User.authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from .serializer import PublishBookSerializer


# Create your views here.



class PublishBookViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 
    pagination_class =CustomPagination
    def list(self, request):
        try:
            books = Book.objects.all()
            if not books:
                return Response({'message': 'No book found', 'data':{}}, status=status.HTTP_200_OK)
            book_data = [
            {
                "book_title": book.title,
                "book_author": book.author,
                "book_likes": book.likes,
                "book_description": book.description,
                "published_by": book.published_by.username if book.published_by else None
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
            book = Book.objects.get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            
            return Response({'message': 'Book Retrive successfully','data':{
                "book_title": book.title,
                "book_author": book.author,
                "book_likes": book.likes,
                "book_description": book.description,
                "published_by": book.published_by.username 
            }}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, pk=None):
        try:
            book = Book.objects.filter(published_by=request.user).get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
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
                book = Book.objects.filter(published_by=request.user).get(pk=pk)
                if not book:
                    return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
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
            book = Book.objects.filter(published_by=request.user).get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            book.delete()
            return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    @action(detail=True, methods=['post'], url_name='like_book')
    def like_book(self, request, book_id=None):
        try:
            # get user
            user=request.user

            book_id = request.query_params.get('book_id')
            if not book_id:
                return Response({'message': 'please provide book id','data':{}}, status=status.HTTP_200_OK)
            book = Book.objects.get(pk=book_id)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            user_profile = Profile.objects.get(user=user)  
            if book_id in user_profile.liked_books:
                return Response({'message': 'Book already liked','data':{}}, status=status.HTTP_200_OK)
            book.likes += 1
            book.save()
            user_profile.liked_books.append(book_id)
            user_profile.save()
            # add the book id in the user profile table
            return Response({'message': 'Book liked successfully','data':{}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],url_name='unlike_book')
    def unlike_book(self, request, pk=None):
        try:
            user=request.user
            book_id = request.query_params.get('book_id')
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
            # user profile
            # get liked_books
            #check if the book id is present or not
            # if present then remove it
            # remove the book id from the user profile table
            return Response({'message': 'Book unliked successfully','data':{}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)