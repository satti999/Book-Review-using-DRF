from django.shortcuts import render
import random
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import User,Book
from .authentication import JWTAuthentication 
from rest_framework.permissions import IsAuthenticated
from .serilizer import UserSignupSerializer, UserLoginSerializer,PublishBookSerializer,AuthSignUpSerializer,VerifyAccountSerializer
from .utils import generate_jwt_token, generate_email_body,send_email
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
            serializer=AuthSignUpSerializer(data=request.data)
            if serializer.is_valid():
                hashed_password = make_password(password)
                signup_data = {
                    "email": serializer.data['email'],
                    "role": serializer.data["role"],
                    "username": serializer.data["username"],
                    "password": hashed_password
                }
                serializer = AuthSignUpSerializer(data=signup_data)
                if serializer.is_valid():
                    otp=random.randint(100000,999999)
                    email_body = generate_email_body(otp)
                     #recipient , subject, body
                    recipient=serializer.data['email']
                    subject="Email Verification"
                    email_sent=send_email(recipient,subject,email_body)
                    if not email_sent:
                        return Response({'error': 'Email not sent' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    serializer.save()
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            data = request.data
            serializer=VerifyAccountSerializer(data=data)
            if serializer.is_valid():
                email=serializer.data['email']
                otp=serializer.data['otp']
                user = User.objects.filter(email=email)
                if not  user.exists():
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                if not user[0].otp==otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            # user[0].is_verified = True
            # user[0].save()
                user=user.first()
                user.is_verified = True
                user.save()
                return Response({'message': 'User verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginViewSet(viewsets.ViewSet):
  
#   @action(detail=False, methods=["post"], url_path="login")
  def create(self, request):
    try:
            serilizer = UserLoginSerializer(data=request.data)
            if serilizer.is_valid():
                    email = serilizer.validated_data['email']
                    password = serilizer.validated_data['password']
                    role = serilizer.validated_data['role']
                    user_role = ['admin', 'user']
                    if role in user_role and 'password' in request.data.keys():
                        user = User.objects.filter(email=email).first()
                        if user is not None:
                            if  check_password(password, user.password):
                                token = generate_jwt_token(email)
                                return Response({"details": "You are successfully logged in",'token': token}, status=status.HTTP_200_OK)
                            else:
                                return Response({"details": "Invalid Password", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"details": "User not found", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                    return Response({"details": "Invalid Provider or Combination provided", "status": "False"}, status=status.HTTP_400_BAD_REQUEST)
           
    except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        




class PublishBookViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 



    def list(self, request):
        try:
            books = Book.objects.filter(published_by=self.request.user)
            if not books:
                return Response({'message': 'No book found', 'data':{}}, status=status.HTTP_200_OK)
            
            serializer = PublishBookSerializer(books, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

      
    def create(self, request):
        try:
            serializer = PublishBookSerializer(data=request.data)
            if serializer.is_valid():
                # self.perform_create(serializer)
                serializer.save(published_by=self.request.user)
                return Response({'message': 'Book published successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
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