from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import User,Book
from .authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from .serilizer import UserSignupSerializer, UserLoginSerializer,PublishBookSerializer
from .utils import generate_jwt_token
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.




class UserSignupViewSet(viewsets.ViewSet):
    
    def create(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists' }, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 8:
                return Response({'error': 'Password must be at least 8 characters long' }, status=status.HTTP_400_BAD_REQUEST)
            serializer=UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                hashed_password = make_password(password)
                signup_data = {
                    "email": serializer.data['email'],
                    "role": serializer.data["role"],
                    "username": serializer.data["username"],
                    "password": hashed_password
                }
                serializer = UserSignupSerializer(data=signup_data)
                serializer.save()
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    


class UserLoginViewSet(viewsets.ViewSet):
        
        def create(self, request):
            try:
                if "email" in request.data:
                    serilizer = UserLoginSerializer(data=request.data)
                    if serilizer.is_valid():
                       email = serilizer.validated_data['email']
                       password = serilizer.validated_data['password']
                       role = serilizer.validated_data['role']
                       user_role = ["admin", "user"]
                       if role in user_role and 'password' in request.data.keys():
                          user = User.objects.filter(email=email).first()
                          if user is not None:
                             if  check_password(password, user.password):
                                token = generate_jwt_token(email)
                                return Response({'token': token}, status=status.HTTP_200_OK)
                             else:
                                return Response({"details": "Invalid Password", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                       else:
                           return Response({"details": "Invalid Password", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                   
                    else:
                        return Response({'details':'Invalid Provider or Combination provided', "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            





class PublishBookViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]  # Use custom JWT authentication
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
      
    def create(self, request):
        try:
            serializer = PublishBookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(published_by=request.user)
                return Response({'message': 'Book published successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        try:
            books = Book.objects.filter(published_by=request.user)
            if not books.exists():
                return Response({'message': 'No book found'}, status=status.HTTP_204_NO_CONTENT)
            serializer = PublishBookSerializer(books, many=True)
            return Response({'message': 'Book Retrive successfully','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.filter(published_by=request.user).get(pk=pk)
            if not book:
                return Response({'message': 'No book found','data':{}}, status=status.HTTP_200_OK)
            serializer = PublishBookSerializer(book)
            return Response({'message': 'Book Retrive successfully','data':serializer.data}, status=status.HTTP_200_OK)
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